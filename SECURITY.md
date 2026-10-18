# Security Policy

## Supported versions

Security fixes are applied to the latest commit on `main`. Older snapshots may not receive fixes.

## Reporting a vulnerability

Please do not publish sensitive details in a public issue. Report the issue privately through the repository's configured security reporting channel. Include:

- affected commit or version
- operating system and Python version
- the smallest reproducible command or project file
- expected and observed behavior
- any logs with secrets removed

Allow time for triage before public disclosure. Do not include Piper model files, private audio, credentials, or personal data in a report.

## Local file and model handling

Audio Forge runs local commands and reads project-local model paths supplied by the user. Review `audioforge.config.json` before running a project, keep model files and generated audio out of public commits when their licenses or contents are not suitable for redistribution, and do not place secrets in project manifests.

