#!/usr/bin/env python3
"""Build an Asterisk language variant from verified EDRAM WAVs."""

import argparse
import csv
import hashlib
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tempfile
import wave

LANGUAGE = "en_CA_nortel"
MAP = Path(__file__).with_name("prompts.csv")
FORMATS = {"wav": None, "ulaw": ("pcm_mulaw", "mulaw"), "alaw": ("pcm_alaw", "alaw")}


def relative_path(value):
    path = PurePosixPath(value)
    if not value or "\\" in value or ":" in value or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Invalid relative path: {value!r}")
    return path


def verify_source(source, expected_hash):
    with wave.open(str(source), "rb") as audio:
        if (audio.getframerate(), audio.getsampwidth(), audio.getnchannels()) != (8000, 2, 1):
            raise ValueError(f"{source}: expected 8 kHz, 16-bit mono PCM")
        frames = audio.readframes(audio.getnframes())
    if hashlib.sha256(frames).hexdigest() != expected_hash:
        raise ValueError(f"{source}: PCM SHA-256 mismatch")


def build(audio_root, output, formats):
    destination = output / LANGUAGE
    if destination.exists() or destination.is_symlink():
        raise ValueError(f"{destination} already exists. Choose a fresh output directory.")
    ffmpeg = shutil.which("ffmpeg")
    if any(FORMATS[fmt] for fmt in formats) and not ffmpeg:
        raise ValueError("FFmpeg is required for ulaw or alaw output.")

    sources = {}
    with MAP.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            if row["status"] != "mapped":
                continue
            prompt = relative_path(row["prompt"])
            if prompt in sources:
                raise ValueError(f"Duplicate mapped prompt: {prompt}")
            source = audio_root / relative_path(row["source_wav"])
            verify_source(source, row["pcm_sha256"])
            sources[prompt] = source

    if not sources:
        raise ValueError("The prompt map has no mapped recordings.")

    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".nortel-", dir=output) as temp:
        staged = Path(temp) / LANGUAGE
        for prompt, source in sources.items():
            for fmt in formats:
                target = staged / f"{prompt}.{fmt}"
                target.parent.mkdir(parents=True, exist_ok=True)
                if fmt == "wav":
                    shutil.copyfile(source, target)
                else:
                    codec, muxer = FORMATS[fmt]
                    subprocess.run(
                        [ffmpeg, "-nostdin", "-loglevel", "error", "-i", str(source),
                         "-c:a", codec, "-f", muxer, str(target)],
                        check=True,
                    )
        staged.rename(destination)
    return destination, len(sources)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("edram_audio", type=Path, help="The audio directory in the EDRAM repository")
    parser.add_argument("output", type=Path, help="Directory in which to build the language folder")
    parser.add_argument("--format", action="append", choices=FORMATS, help="Repeat to add formats. Default: wav.")
    args = parser.parse_args()
    formats = tuple(dict.fromkeys(args.format or ["wav"]))
    try:
        destination, count = build(args.edram_audio, args.output, formats)
    except (OSError, EOFError, ValueError, wave.Error, subprocess.CalledProcessError) as error:
        parser.exit(1, f"error: {error}\n")
    print(f"Built {count} prompts in {', '.join(formats)} at {destination}")


if __name__ == "__main__":
    main()
