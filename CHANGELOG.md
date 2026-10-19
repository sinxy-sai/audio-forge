# Changelog

All notable changes to Audio Forge are documented here.

## [0.3.1] - 2026-10-19

### Fixed

- Replaced the removed Python `audioop` dependency in reference-audio inspection so the release smoke test works on current Python versions.

## [0.3.0] - 2026-10-19

### Added

- Added local CosyVoice zero-shot voice cloning with WAV/`.lab` reference discovery.
- Added `clone-candidates` and `generate voice-clone` CLI workflows.
- Added project-local CosyVoice configuration and isolated worker execution.

### Documentation

- Documented generic `assets/reference-audio/<speaker>/` and `models/` work-project layout.
- Updated local voice-model and project-configuration guidance.

## [Unreleased]

### Documentation

- Added local voice, voice-cloning, speech-recognition, model-size, and ONNX selection guidance.
- Added the `transcribe` CLI command with faster-whisper project analysis outputs.

## [0.2.0] - 2026-10-18

### Added

- Separated CLI argument parsing from command execution.
- Added project-local `VoiceConfig` resolution for Piper.
- Added repository security, contribution conduct, and changelog documentation.
- Moved release-only maintenance scripts under `.github/scripts/`.

### Changed

- Voice rendering now passes a validated executable and model into the Piper backend.
- Error messages identify the missing project configuration or file directly.
- Removed repository helper scripts; CLI smoke checks now use `python -m audioforge`.

### Added

- Local-first CLI for procedural music, sound effects, and Piper voice projects.
- `AudioProject` manifest and browser protocol reference.
- Project-local `audioforge.config.json` support.
- WAV inspection and optional FFmpeg export commands.

## [0.1.0]

### Added

- Dependency-free tone and UI confirmation examples.
- Reproducible WAV inspection utilities.
- Initial Codex skill guidance and presets.

