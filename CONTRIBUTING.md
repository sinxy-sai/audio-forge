# Contributing to Audio Forge

Contributions are welcome for clearer skill guidance, better standard-library synthesis examples, and reliable WAV inspection.

Keep implementation code under `audioforge/`, user-facing references under `references/`, small editable examples under `examples/`, and release-only maintenance scripts under `.github/scripts/`.

## Before opening a change

- Keep the default workflow dependency-free and local.
- Keep generated audio source editable and reproducible.
- Do not add copyrighted samples or files whose redistribution rights are unclear.
- Keep the skill focused on local music, sound-effect, and Piper voice WAV projects.
- Update the README when a command, file, or installation path changes.
- Keep Piper paths in project-local `audioforge.config.json`; do not add system environment configuration to the skill.
- Do not assume or create a virtual environment as part of the skill; document any optional local setup separately.
- Update `CHANGELOG.md` under `Unreleased` when behavior or user-facing commands change.

## Local checks

From the repository root, run:

```powershell
python -m audioforge generate sfx --brief "contributing smoke click" --duration 0.25 --output "$env:TEMP\audio-forge-contributing"
python -m audioforge inspect "$env:TEMP\audio-forge-contributing\renders\sfx.wav" --fail-on-clip
python -m audioforge doctor
```

Also run the Codex skill validator when editing `SKILL.md` or `agents/openai.yaml`:

```powershell
python <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py .
```

Before opening a pull request, run `python -m compileall -q audioforge`, the skill validator, and the relevant CLI smoke commands.

## Pull requests

Explain the user scenario, the files changed, and the commands used to verify the result. Use a focused Conventional Commit subject such as `feat: add impact sound example` or `fix: report mono WAV peak correctly`.

Please follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) and report security issues privately as described in [SECURITY.md](SECURITY.md).
