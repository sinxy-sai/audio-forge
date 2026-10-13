# Audio Forge

Audio Forge is a Codex skill for creating short music cues and sound effects as reproducible, editable WAV projects.

It turns a natural-language brief into a small Python synthesis project. The default path uses only the Python standard library, writes PCM WAV, and keeps the source script beside the rendered audio.

## What it supports

- Short background cues and loopable musical ideas
- UI clicks, confirmations, warnings, impacts, rises, and whooshes
- 16-bit PCM WAV output
- 44.1 kHz by default, with configurable sample rate and channel count
- Output inspection for duration, format, peak level, and clipping

Audio Forge is intended for prototypes and game/product assets. It does not provide MIDI or DAW export, external audio-model calls, downloaded samples, or professional mastering.

## Install as a Codex skill

Clone or copy this repository into a Codex skills directory and keep the folder name `audio-forge`:

```powershell
git clone https://github.com/sinxy-sai/audio-forge.git "$HOME/.codex/skills/audio-forge"
```

For a project-local installation, copy the repository to:

```text
<project>/.agents/skills/audio-forge/
```

Restart or refresh Codex after installing so it can discover the skill.

## Use the skill

Ask Codex for a concrete audio task, for example:

```text
Use Audio Forge to create a 0.4 second confirmation sound for a game UI.
Make it bright, with two rising tones, render a WAV, keep the Python source,
and inspect the output for clipping.
```

For a music cue:

```text
Use Audio Forge to create an 8 second loopable sci-fi background cue.
Use a restrained low pulse, suspended tones, and a short rising motif.
Render a 44.1 kHz stereo WAV and keep the editable source script.
```

The skill will ask for missing details when they materially affect the result and will state any defaults it uses.

## Included tools

```text
scripts/synth_tone.py   Minimal dependency-free WAV generator
scripts/inspect_wav.py  WAV metadata, peak, and clipping inspector
references/presets.md   Starting points for common music and effect types
examples/ui_confirm.py  Small editable confirmation-effect example
```

Run the tools directly from the repository:

```powershell
python scripts/synth_tone.py renders/tone.wav --frequency 440 --duration 0.5
python scripts/inspect_wav.py renders/tone.wav --fail-on-clip
python examples/ui_confirm.py renders/ui-confirm.wav
python scripts/inspect_wav.py renders/ui-confirm.wav --fail-on-clip
```

All commands use Python's standard library and do not require package installation.

## Output layout

Generated projects should keep the brief, source, render, and delivery notes together:

```text
project/
|-- brief.md
|-- source/
|   `-- *.py
|-- renders/
|   `-- *.wav
`-- README.md
```

## License

Audio Forge is released under the [MIT License](LICENSE).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution workflow and quality checks.
