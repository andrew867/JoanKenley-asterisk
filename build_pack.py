#!/usr/bin/env python3
"""Build an Asterisk language variant from verified Nortel WAVs."""

import argparse
from array import array
import csv
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import struct
import subprocess
import sys
import tarfile
import tempfile
import wave

LANGUAGE = "en_CA_nortel"
MAP = Path(__file__).with_name("prompts.csv")
STOCK_SHA256 = "07ad543764567ea235d3a96dcd15ecce4521855efc295de6f5443299c331ec0b"
FORMATS = {"wav": None, "ulaw": ("pcm_mulaw", "mulaw"), "alaw": ("pcm_alaw", "alaw")}


def relative_path(value):
    path = PurePosixPath(value)
    if not value or "\\" in value or ":" in value or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Invalid relative path: {value!r}")
    return path


def verify_source(stream, name, expected_hash=None):
    with wave.open(stream, "rb") as audio:
        if (audio.getframerate(), audio.getsampwidth(), audio.getnchannels()) != (8000, 2, 1):
            raise ValueError(f"{name}: expected 8 kHz, 16-bit mono PCM")
        frames = audio.readframes(audio.getnframes())
    digest = hashlib.sha256(frames).hexdigest()
    if expected_hash and digest != expected_hash:
        raise ValueError(f"{name}: PCM SHA-256 mismatch")
    return digest


def read_map():
    with MAP.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    ids = [relative_path(row["prompt"]) for row in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate Asterisk prompt ID")
    return zip(ids, rows)


def add_stock_sources(path, missing, staging, sources):
    with path.open("rb") as stream:
        digest = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != STOCK_SHA256:
        raise ValueError("Stock archive does not match Asterisk English Core Sounds 1.6.1")

    expected = {f"{prompt}.wav": prompt for prompt in missing}
    notices = {"LICENSE-asterisk-core-en-1.6.1", "CREDITS-asterisk-core-en-1.6.1"}
    with tarfile.open(path, "r|gz") as archive:
        for entry in archive:
            if not entry.isfile():
                continue
            if entry.name in notices:
                with archive.extractfile(entry) as original:
                    (staging.parent / entry.name).write_bytes(original.read())
                notices.remove(entry.name)
                continue
            if entry.name not in expected:
                continue
            prompt = expected.pop(entry.name)
            relative = relative_path(entry.name)
            target = staging / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.extractfile(entry) as original, target.open("wb") as out:
                shutil.copyfileobj(original, out)
            sources[prompt] = (target, {"source": "asterisk-stock", "source_wav": str(relative),
                                        "pcm_sha256": verify_source(str(target), target)})
    if expected or notices:
        raise ValueError(f"Missing stock archive member: {next(iter(expected or notices))}")


def select_sources(audio_root, callpilot_audio, bcm_audio, stock_archive, staging):
    roots = {"edram": audio_root, "callpilot5": callpilot_audio, "bcm4": bcm_audio}
    sources = {}
    missing = []
    for prompt, row in read_map():
        origin = row.get("source") or "edram"
        if origin not in roots:
            raise ValueError(f"Unknown source {origin!r} for {prompt}")
        if row["status"] == "mapped" and roots[origin] is not None:
            location = relative_path(row["source_wav"])
            source = roots[origin] / location
            expected = row["pcm_sha256"]
            if not re.fullmatch(r"[0-9a-f]{64}", expected):
                raise ValueError(f"{prompt}: mapped clip needs a PCM SHA-256")
            digest = verify_source(str(source), source, expected)
            sources[prompt] = (source, {"source": origin, "source_wav": str(location), "pcm_sha256": digest})
        elif row["scope"] == "core":
            missing.append(prompt)
    if stock_archive:
        add_stock_sources(stock_archive, missing, staging, sources)
    return sources


def g711_tables(ffmpeg, formats):
    signal = struct.pack("<65536H", *range(65536))
    tables = {}
    for fmt in formats:
        if FORMATS[fmt] is None:
            continue
        codec, muxer = FORMATS[fmt]
        result = subprocess.run(
            [ffmpeg, "-nostdin", "-loglevel", "error", "-f", "s16le", "-ar", "8000", "-ac", "1",
             "-i", "pipe:0", "-c:a", codec, "-f", muxer, "pipe:1"],
            input=signal, stdout=subprocess.PIPE, check=True,
        ).stdout
        if len(result) != 65536:
            raise ValueError(f"FFmpeg returned an invalid {fmt} conversion table")
        tables[fmt] = result
    return tables


def write_prompt(source, target, formats, tables):
    if "wav" in formats:
        shutil.copyfile(source, target.with_name(target.name + ".wav"))
    if not tables:
        return
    samples = array("H")
    with wave.open(str(source), "rb") as audio:
        samples.frombytes(audio.readframes(audio.getnframes()))
    if sys.byteorder != "little":
        samples.byteswap()
    for fmt, table in tables.items():
        target.with_name(f"{target.name}.{fmt}").write_bytes(bytes(table[value] for value in samples))


def build(audio_root, output, formats, *, callpilot_audio=None, bcm_audio=None, stock_archive=None):
    destination = output / LANGUAGE
    if destination.exists() or destination.is_symlink():
        raise ValueError(f"{destination} already exists. Choose a fresh output directory.")
    ffmpeg = shutil.which("ffmpeg")
    if any(FORMATS[fmt] for fmt in formats) and not ffmpeg:
        raise ValueError("FFmpeg is required for ulaw or alaw output.")

    tables = g711_tables(ffmpeg, formats) if any(FORMATS[fmt] for fmt in formats) else {}
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".nortel-", dir=output) as temp:
        staged = Path(temp) / LANGUAGE
        sources = select_sources(audio_root, callpilot_audio, bcm_audio, stock_archive, Path(temp) / "stock")
        if not sources:
            raise ValueError("The prompt map has no available recordings.")
        for prompt, (source, _) in sources.items():
            target = staged / prompt
            target.parent.mkdir(parents=True, exist_ok=True)
            write_prompt(source, target, formats, tables)
        for notice in Path(temp).glob("*-asterisk-core-en-1.6.1"):
            shutil.copyfile(notice, staged / notice.name)
        manifest = {"language": LANGUAGE, "formats": list(formats),
                    "prompts": {str(prompt): info for prompt, (_, info) in sources.items()}}
        (staged / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n",
                                               encoding="utf-8", newline="\n")
        staged.rename(destination)
    return destination, len(sources)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("edram_audio", type=Path, help="The audio directory in the EDRAM repository")
    parser.add_argument("output", type=Path, help="Directory in which to build the language folder")
    parser.add_argument("--callpilot-audio", type=Path, help="CallPilot 5.0 Canadian English extraction root")
    parser.add_argument("--bcm-audio", type=Path, help="BCM 4.0 extraction build directory")
    parser.add_argument("--stock-archive", type=Path, help="Fill remaining core IDs from the pinned English WAV archive")
    parser.add_argument("--format", action="append", choices=FORMATS, help="Repeat to add formats. Default: wav.")
    args = parser.parse_args()
    formats = tuple(dict.fromkeys(args.format or ["wav"]))
    try:
        destination, count = build(args.edram_audio, args.output, formats,
                                   callpilot_audio=args.callpilot_audio, bcm_audio=args.bcm_audio,
                                   stock_archive=args.stock_archive)
    except (OSError, EOFError, ValueError, wave.Error, tarfile.TarError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"error: {error}\n")
    print(f"Built {count} prompts in {', '.join(formats)} at {destination}")


if __name__ == "__main__":
    main()
