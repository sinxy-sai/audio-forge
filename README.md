# Audio Forge

Audio Forge is a local-first Codex skill for creating short music cues, sound effects, and Piper-backed voice projects as reproducible, editable WAV projects.

It turns a natural-language brief into an `AudioProject`. Procedural music and effects use the Python standard library; voice uses a project-local Piper executable and voice model. Each project keeps its brief, manifest, parameters, render, and inspection data together.

## What it supports

- Short background cues and loopable musical ideas
- UI clicks, confirmations, warnings, impacts, rises, and whooshes
- Local Piper voice rendering
- Optional local faster-whisper transcription with timestamped project analysis
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
Make it bright, with two rising tones, render a WAV, keep the project parameters,
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
    "executable": ".venv/Scripts/piper.exe",
    "model": "models/voices/zh_CN.onnx"
  }
}
```

Then ask:

```text
Use Audio Forge to render the Chinese voice line “任务完成” with the local Piper voice model. Keep the AudioProject manifest and inspect the WAV.
```

## Core CLI and package

```text
audioforge/             Local-first CLI and backend adapters
references/             Presets, project protocol, and project configuration
examples/               Small editable code examples
.github/scripts/        Release-only validation and notes helpers
```

The Python package is intentionally split by responsibility:

```text
audioforge/
|-- cli.py        argument parsing only
|-- commands.py   command orchestration
|-- config.py     project-local configuration
|-- project.py    AudioProject files
|-- procedural.py music and sound effects
|-- piper.py      Piper voice backend
|-- transcribe.py faster-whisper transcription backend
`-- wav.py        PCM WAV writing and inspection
```

Run the CLI from the repository root:

```powershell
python -m audioforge generate sfx --brief "bright confirmation click" --duration 0.2 --output "$env:TEMP\audio-forge-sfx"
python -m audioforge inspect "$env:TEMP\audio-forge-sfx\renders\sfx.wav" --fail-on-clip
python examples/ui_confirm.py "$env:TEMP\audio-forge-ui-confirm.wav"
python -m audioforge inspect "$env:TEMP\audio-forge-ui-confirm.wav" --fail-on-clip
python -m audioforge doctor
python -m audioforge transcribe --audio .\audioforge-real-demo\whisper-input\renders\voice.wav --output .\audioforge-real-demo\whisper-input --config .\audioforge-real-demo\audioforge.config.json --language zh
```

Procedural commands use Python's standard library and do not require package installation. Audio Forge does not create a `.venv` automatically. Voice generation additionally requires a Piper executable and voice model available to the work project and configured in `audioforge.config.json`.

For local voice and speech-recognition model choices, see [references/voice-model-selection.md](references/voice-model-selection.md). Piper and faster-whisper are integrated as local backends. CosyVoice remains a planned voice-cloning backend, and no model is downloaded automatically.

Voice rendering defaults to Piper volume `0.95` so the generated WAV keeps headroom. Override it with `--volume` when needed.

## License

Audio Forge is released under the [MIT License](LICENSE).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution workflow and quality checks.

See [SECURITY.md](SECURITY.md) for vulnerability reporting and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for participation standards.
