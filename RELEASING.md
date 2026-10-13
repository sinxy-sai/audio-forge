# Releasing Audio Forge

Audio Forge releases are created from SemVer tags:

```text
v0.1.0-alpha.1
v0.1.0-beta.1
v0.1.0
v0.1.1
```

Alpha and beta tags are published as regular GitHub Releases. The release workflow does not set the prerelease flag.

## Create a release

1. Make sure `main` is clean and up to date.
2. Run the local checks:

   ```powershell
   python tools/release/validate_skill.py v0.1.0-alpha.1
   python -m py_compile scripts\synth_tone.py scripts\inspect_wav.py examples\ui_confirm.py tools\release\validate_skill.py tools\release\generate_release_notes.py
   python scripts\synth_tone.py renders\release-smoke.wav --frequency 440 --duration 0.25 --channels 1
   python scripts\inspect_wav.py renders\release-smoke.wav --fail-on-clip
   Remove-Item renders\release-smoke.wav
   ```

3. Create and push the tag:

   ```powershell
   git tag -a v0.1.0-alpha.1 -m "release: v0.1.0-alpha.1"
   git push origin v0.1.0-alpha.1
   ```

4. The `Release Audio Forge` workflow validates the tag, runs the smoke test, builds complete tracked-source archives, generates notes, and creates the GitHub Release.

## Release assets

Each release contains:

- `audio-forge-<tag>.tar.gz`
- `audio-forge-<tag>.zip`
- `SHA256SUMS.txt`

The archives are created with `git archive` from the tag. Private local files under `docs/private/`, `.git`, ignored audio renders, and untracked files are not included.

## Release notes

`tools/release/generate_release_notes.py` groups Conventional Commit subjects into Highlights, Fixes, and Documentation and maintenance. It also includes validation results, installation instructions, release asset names, and a complete first-parent changelog.

The source template is kept at `.github/release-notes-template.md`; the generated note is the authoritative text attached to each release.
