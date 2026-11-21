# JoanKenley-asterisk

**First alpha** · [v0.1.0-alpha.1](https://github.com/andrew867/JoanKenley-asterisk/releases/tag/v0.1.0-alpha.1) · [Release notes](CHANGELOG.md)

Asterisk English prompts assembled from Nortel DMS, CallPilot 5.0 Canadian English and BCM 4.0 recordings. The repository name is the project title. The source and PCM hash are recorded per clip. Individual voice credits remain unverified.

## Coverage

[The master checklist](prompts.csv) tracks all 568 WAV IDs in Asterisk English Core Sounds 1.6.1 and 94 Nortel additions.

| Asterisk core source | IDs |
| --- | ---: |
| Nortel DMS | 38 |
| CallPilot 5.0 | 56 |
| BCM 4.0 | 47 |
| Stock English fallback | 427 |
| **Total** | **568** |

Nortel recordings cover digits, teens and round tens through ninety, weekdays, months, ordinals, letters and some voicemail prompts. The 94 additional IDs include Canadian and U.S. intercepts, CLASS, call return and tone recordings. The SIT IDs use the directly decoded ESTD0AA samples and menu timing.

The checklist marks stock silence as `stock` and the remaining stock fallback IDs as `missing`. Those IDs use the Asterisk originals in a complete build. Voicemail decisions follow the actual action called for by Asterisk, including its keys. The mapped password clips say “number sign” for the pound key. The notes record source IDs and wording differences. Prompts that depend on Asterisk-specific instructions, such as conference menus, use stock English. [Asterisk sample voicemail configuration](https://github.com/asterisk/asterisk/blob/master/configs/samples/voicemail.conf.sample)

## Install the alpha pack

Download [en_CA_nortel.zip](https://github.com/andrew867/JoanKenley-asterisk/releases/download/v0.1.0-alpha.1/en_CA_nortel.zip), extract it, and copy the `en_CA_nortel` folder into the Asterisk sounds directory. Set `CHANNEL(language)=en_CA_nortel` on a test channel. The [example dialplan](examples/extensions.conf) plays digits and a Canadian intercept.

The ZIP contains 662 prompt IDs in WAV, μ-law and A-law, along with a per-file source manifest and the Asterisk stock audio license and credits. Its SHA-256 is `012404842e8089bf3764cbd0a0182b8d3b5cf7f4d45c8d98b5e2d6bb218ee648`.

## Build the language directory

Use Python 3.10 or newer. Install FFmpeg for μ-law and A-law output. The build verifies the source PCM hashes and writes a per-prompt source manifest.

1. Use the current [EDRAM audio export](https://github.com/andrew867/EDRAM/tree/6c19f5c65d6d55d54cc6a98ba31092436672ce15/audio).
2. Export Canadian English from the CallPilot 5.0 language CD. [CallPilot 5.0 extraction guide](https://github.com/andrew867/CallPilotPrompts/blob/main/CALLPILOT5_FORMAT.md)
3. Export BCM American English to `build/bcm4-en-us` and the IVR numset to `build/bcm4-mmf/numset`. [BCM extraction commands](https://github.com/andrew867/CallPilotPrompts#extract-bcm-40-audio)
4. Download the official 1.6.1 WAV archive to fill the remaining core IDs. [Asterisk English Core Sounds](https://downloads.asterisk.org/pub/telephony/sounds/releases/asterisk-core-sounds-en-wav-1.6.1.tar.gz)

~~~sh
python build_pack.py ../EDRAM/audio build/sounds \
  --callpilot-audio ../CallPilotPrompts/build/callpilot5-en-ca \
  --bcm-audio ../CallPilotPrompts/build \
  --stock-archive ../asterisk-core-sounds-en-wav-1.6.1.tar.gz \
  --format wav --format ulaw --format alaw
~~~

The full build contains **662 prompt IDs**. Omit `--stock-archive` to let Asterisk use its installed English fallbacks. Omit either CallPilot or BCM input to build using the remaining sources. An output language directory must be new. The Asterisk archive SHA-256 is `07ad543764567ea235d3a96dcd15ecce4521855efc295de6f5443299c331ec0b`.

Copy `en_CA_nortel` into the sounds directory on an Asterisk instance and choose that language on a channel. The [example dialplan](examples/extensions.conf) plays a test number and a Canadian intercept. The built language directory contains `manifest.json` and, with the stock archive, its original license and credits. The original vendor media stays local. [Asterisk language fallback order](https://docs.asterisk.org/Deployment/Internationalization-and-Localization/Sound-Prompt-Searching-based-on-Channel-Language/)
