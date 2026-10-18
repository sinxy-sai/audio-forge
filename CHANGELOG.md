# Changelog

All notable changes to Audio Forge are documented here.

## [Unreleased]

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

