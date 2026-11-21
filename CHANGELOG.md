# Nortel Asterisk prompts 0.1.0 alpha 1

First tagged release of the Asterisk prompt map and local sound-pack builder for Nortel recordings.

- Track all 568 Asterisk English Core Sounds 1.6.1 IDs and 94 Nortel additions. The core map uses 141 Nortel clips and 427 stock prompts in a full build.
- Build the `en_CA_nortel` language directory in WAV, μ-law and A-law. The builder verifies the source PCM and writes a manifest with the origin of each file.
- Try the example dialplan for digit playback and a Canadian intercept.

## Try it

Download [en_CA_nortel.zip](https://github.com/andrew867/JoanKenley-asterisk/releases/download/v0.1.0-alpha.1/en_CA_nortel.zip), extract it, and copy `en_CA_nortel` into the Asterisk sounds directory. Set `CHANNEL(language)=en_CA_nortel` on a test channel. The ZIP includes the per-file source manifest and stock Asterisk audio credits. The source archive contains the builder and mappings.

The reference build verified 1,986 audio files across three formats. Live calls and individual speaker credits remain unverified.

[Build guide](README.md) · [Prompt checklist](prompts.csv) · [Example dialplan](examples/extensions.conf)
