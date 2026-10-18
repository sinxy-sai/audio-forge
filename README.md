# Audio Forge

Audio Forge is a local-first Codex skill for creating short music cues, sound effects, and Piper-backed voice projects as reproducible, editable WAV projects.

It turns a natural-language brief into an `AudioProject`. Procedural music and effects use the Python standard library; voice uses a locally installed Piper executable and voice model. Each project keeps its brief, manifest, parameters, render, and inspection data together.

## What it supports

- Short background cues and loopable musical ideas
- UI clicks, confirmations, warnings, impacts, rises, and whooshes
- Local Piper voice rendering
- 16-bit PCM WAV output
- 44.1 kHz by default, with configurable sample rate and channel count
- Output inspection for duration, format, peak level, and clipping

Audio Forge is intended for prototypes and game/product assets. It does not provide Blender integration, MIDI or DAW export, cloud audio calls, automatic model/sample downloads, or professional mastering.

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
Render a 44.1 kHz stereo WAV and keep the editable project parameters.
```

The skill will ask for missing details when they materially affect the result and will state any defaults it uses.

For a local voice project, add `audioforge.config.json` to the work project. Its paths are relative to that project:

```json
{
  "voice": {
    "backend": "piper",
    "executable": "tools/piper/piper.exe",
    "model": "models/voices/zh_CN.onnx"
  }
}
```

Then ask:

```text
Use Audio Forge to render the Chinese voice line “任务完成” with the local Piper voice model. Keep the AudioProject manifest and inspect the WAV.
```

## Included tools

```text
scripts/synth_tone.py   Minimal dependency-free WAV generator
scripts/inspect_wav.py  WAV metadata, peak, and clipping inspector
audioforge/             Local-first CLI and backend adapters
references/presets.md   Starting points for common music and effect types
examples/ui_confirm.py  Small editable confirmation-effect example
```

Run the tools directly from the repository:

```powershell
python scripts/synth_tone.py renders/tone.wav --frequency 440 --duration 0.5
python scripts/inspect_wav.py renders/tone.wav --fail-on-clip
python examples/ui_confirm.py renders/ui-confirm.wav
python scripts/inspect_wav.py renders/ui-confirm.wav --fail-on-clip
python -m audioforge doctor
```

Procedural commands use Python's standard library and do not require package installation. Voice generation additionally requires the work project's Piper executable and voice model configured in `audioforge.config.json`.

## Output layout

Generated projects should keep the brief, manifest, source parameters, render, and delivery notes together:

```text
project/
|-- project.json
|-- brief.md
|-- source/
|   `-- parameters.json
|-- renders/
|   `-- *.wav
|-- metadata/
|   `-- backend.json
`-- README.md
```

The `project.json` layout is documented in `references/project-protocol.md` and is reserved for a future browser editor.

## License

Audio Forge is released under the [MIT License](LICENSE).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution workflow and quality checks.
