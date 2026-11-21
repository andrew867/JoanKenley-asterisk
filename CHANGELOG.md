# Nortel Asterisk prompts 0.1.0 alpha 1

First tagged release of the Asterisk prompt map and local sound-pack builder for Nortel recordings.

- Track all 568 Asterisk English Core Sounds 1.6.1 IDs and 94 Nortel additions. The core map uses 141 Nortel clips and 427 stock prompts in a full build.
- Build the `en_CA_nortel` language directory in WAV, μ-law and A-law. The builder verifies the source PCM and writes a manifest with the origin of each file.
- Try the example dialplan for digit playback and a Canadian intercept.

## Try it

Download **Source code (zip)** and follow the README to assemble the inputs. A full build uses the EDRAM WAV archive, locally decoded CallPilot and BCM files, and the official Asterisk 1.6.1 WAV archive. A smaller build can rely on Asterisk's installed English fallback.

The reference build verified 1,986 audio files across three formats. Live calls and individual speaker credits remain unverified. Generated audio packs are built locally from source recordings.

[Build guide](README.md) · [Prompt checklist](prompts.csv) · [Example dialplan](examples/extensions.conf)
