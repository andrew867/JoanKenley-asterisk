# JoanKenley-asterisk

A local Asterisk sound pack built from Nortel DMS recordings, with a prompt checklist for matching future CallPilot samples. The repository name is the project title. Voice credits for individual DMS loads remain unverified.

## Prompt coverage

[Open the master checklist](prompts.csv). It has one row per WAV prompt ID in the official Asterisk English Core Sounds 1.6.1 archive, plus the Nortel extensions under `nortel/`. A mapped row contains the source path relative to EDRAM's `audio/` directory and the SHA-256 of the decoded PCM. The prompts in a composite announcement keep their original wording and timing.

| Scope | Status | Count |
| --- | --- | ---: |
| Asterisk core | DMS mapping | 38 |
| Asterisk core | Unmapped | 520 |
| Asterisk core | Stock silence | 10 |
| Nortel additions | Mapped | 94 |

Filter `status` to `missing` and `group` to `voicemail` for the first CallPilot review set. The checklist has 114 such rows. A candidate needs to match the Asterisk menu action and wording. Use the `core-sounds-en.txt` transcript included in the [official 1.6.1 WAV archive](https://downloads.asterisk.org/pub/telephony/sounds/releases/asterisk-core-sounds-en-wav-1.6.1.tar.gz) to see the upstream wording for each stock ID.

Current recordings cover standard digits, ten through nineteen, tens up to fifty, the months, and a.m./p.m. The extra prompts include Canadian and U.S. call treatments, CLASS and call return, as well as SIT, the calling-card bong, milliwatt, and receiver-off-hook tones. Full Nortel intercepts have their own IDs. For example, `nortel/ca/vacant-code` includes a complete spoken treatment, while Asterisk's `cannot-complete-as-dialed` is a single sentence.

## Build and try it

Use Python 3.10 or newer and the [EDRAM audio export](https://github.com/andrew867/EDRAM/tree/8f6a2b3d157b20c6afadd1004606d5497c4e5c5a/audio). FFmpeg is needed for G.711 output. WAV-only builds use the standard library.

```sh
python build_pack.py ../EDRAM/audio build/sounds --format wav --format ulaw --format alaw
```

Copy the resulting `en_CA_nortel` folder into the sounds directory of a lab Asterisk instance. Choose `en_CA_nortel` on a channel to use the mappings and let Asterisk [fall back to the installed English prompts](https://docs.asterisk.org/Deployment/Internationalization-and-Localization/Sound-Prompt-Searching-based-on-Channel-Language/) for the gaps. The [example dialplan](examples/extensions.conf) plays a test number using the DMS digits and plays a Canadian intercept with SIT as early media. Include its context from a lab endpoint.

The WAVs preserve the decoded 8 kHz, 16-bit mono PCM. The raw `.ulaw` and `.alaw` files are G.711 derivatives for Asterisk. Each build verifies PCM hashes before writing, and requires a fresh language directory. The archived recordings keep the [source archive's provenance](https://github.com/andrew867/EDRAM/blob/main/data/README.md).

## Source revisions

- Asterisk English Core Sounds 1.6.1 WAV archive, SHA-256 `07ad543764567ea235d3a96dcd15ecce4521855efc295de6f5443299c331ec0b`. The baseline comes from its 568 WAV member names.
- [andrew867/EDRAM at 8f6a2b3](https://github.com/andrew867/EDRAM/tree/8f6a2b3d157b20c6afadd1004606d5497c4e5c5a). The [Nortel phrase catalog](https://github.com/andrew867/EDRAM/blob/8f6a2b3d157b20c6afadd1004606d5497c4e5c5a/references/nortel-phrases.csv) identifies the numbers, time fragments and feature prompts.
- [CallPilotPrompts](https://github.com/andrew867/CallPilotPrompts) tracks factory prompt formats and conversion.
