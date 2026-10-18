# Contributing to Audio Forge

Contributions are welcome for clearer skill guidance, better standard-library synthesis examples, and reliable WAV inspection.

## Before opening a change

- Keep the default workflow dependency-free and local.
- Keep generated audio source editable and reproducible.
- Do not add copyrighted samples or files whose redistribution rights are unclear.
- Keep the skill focused on local music, sound-effect, and Piper voice WAV projects.
- Update the README when a command, file, or installation path changes.
- Keep Piper paths in project-local `audioforge.config.json`; do not add system environment configuration to the skill.

## Local checks

From the repository root, run:

```powershell
python scripts/synth_tone.py renders/contributing-smoke.wav --frequency 440 --duration 0.25
python scripts/inspect_wav.py renders/contributing-smoke.wav --fail-on-clip
python -m audioforge doctor
```

Also run the Codex skill validator when editing `SKILL.md` or `agents/openai.yaml`:

```powershell
python <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py .
```

Remove generated files under `renders/` before committing unless they are intentionally documented examples.

## Pull requests

Explain the user scenario, the files changed, and the commands used to verify the result. Use a focused Conventional Commit subject such as `feat: add impact sound example` or `fix: report mono WAV peak correctly`.
