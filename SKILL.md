---
name: audio-forge
description: Create local-first music, sound effects, and Piper voice WAV projects from a brief, with editable parameters, inspectable renders, and a stable AudioProject manifest. Use for local audio assets and prototypes; do not use for Blender workflows, cloud audio APIs, MIDI/DAW projects, or professional mastering.
metadata:
  short-description: Create reproducible music, sound-effect, and Piper voice WAV projects
---

# Audio Forge

Use this skill to turn a music, sound-effect, or voice brief into a small, editable, locally rendered WAV project.

## Operating boundary

- Use Python's standard library by default. Do not install packages or download samples unless the user explicitly asks for a different workflow.
- Piper is the only voice backend currently provided. Resolve its executable and voice model from the work project's `audioforge.config.json`; do not use system environment variables or make it a dependency of music or sound-effect tasks.
- Produce an editable `project.json` and source parameters alongside the WAV so the result can be regenerated.
- This skill creates prototypes and game/product assets. Do not describe the output as professional mastering or guaranteed commercial-release audio.
- Do not call external audio-generation services, upload files, or publish output without explicit user instructions.
- Keep the user's requested duration, format, and loop behavior exact when they are provided.
- Treat the caller's current working directory as the workspace root. The skill installation directory is read-only reference material, never an output directory.
- Never create generated audio, source scripts, briefs, README files, or project folders inside the skill installation directory, including its `scripts/`, `references/`, `agents/`, or `examples/` folders.

## Workflow

1. Classify the request as **music**, **sound effect**, or **voice**.
2. Extract the brief: purpose, text if voice, duration, mood, style, pitch or tempo, main timbres, loop requirement, sample rate, channel count, and output location.
3. Ask only for missing details that materially affect the result. Otherwise use these defaults and state them: 44,100 Hz, 16-bit PCM WAV, stereo for music, mono for short effects, and a short fade-in/fade-out to prevent clicks.
4. Resolve the output root before creating files. If the user gives an output path, resolve a relative path from the caller's current working directory. Otherwise create a project directory named from the user's requested asset under the caller's current working directory, for example `bundle/jump-effect/`. State the absolute output root before rendering.

   ```text
   <caller-current-working-directory>/<project-slug>/
   ```

   Do not use the skill directory as a fallback when the requested name or output path is missing; ask for the missing project name or use a clearly stated slug under the caller's current working directory.

5. Create the project with:

   ```text
   project/
   |-- project.json
   |-- brief.md
   |-- source/
   |   `-- parameters.json
   |-- renders/
   |   `-- *.wav
   `-- README.md
   ```

   If the user only requests a quick preview, the project manifest and WAV may be placed directly in the requested folder.

6. For music and effects, use `python -m audioforge generate`; keep parameters in `source/parameters.json` and the manifest in `project.json`.
7. For voice, use `python -m audioforge generate voice` with the work project's `audioforge.config.json`. The default Piper volume is `0.95` to leave headroom; change it only when the brief requires a different level. If the project config or Piper files are unavailable, report the exact project path that is missing; do not silently switch to a cloud service.
8. Inspect the actual output with `scripts/inspect_wav.py` or `python -m audioforge inspect`. Report duration, sample rate, bit depth, channels, peak level, and clipping count. If clipping is present, lower the gain and render again unless the user explicitly requested a clipped/lo-fi effect.
9. Report absolute paths to the project, WAV, and parameters, plus the checks that were run. Mention any defaults or limitations that affected the result.

## Music mode

Use a simple timeline: intro, motif or groove, variation, and ending/loop tail. Choose a small number of voices and leave headroom. For a loop, make the first and last bars share tempo, tonal center, and compatible ambience; inspect the boundary rather than assuming it is seamless.

## Sound-effect mode

Describe the event and its perceived action before choosing parameters. Combine a few purposeful layers, for example:

- UI click: short high-frequency transient plus a quiet body tone.
- Confirm: two rising tones with a short decay.
- Warning: repeated or alternating tones with restrained low end.
- Impact: a pitch-dropping sine or triangle plus a brief noise burst.
- Whoosh: filtered or shaped noise with a frequency glide.

Keep effects short and leave a clean tail. Use stereo movement only when it supports the event.

## Supporting resources

- Read [references/presets.md](references/presets.md) when choosing a starting point for a common music or sound-effect type.
- Use [scripts/synth_tone.py](scripts/synth_tone.py) as a dependency-free WAV generation example.
- Use [scripts/inspect_wav.py](scripts/inspect_wav.py) after every render to verify the file that was actually written.
- Read [references/project-protocol.md](references/project-protocol.md) when a task needs to exchange an AudioProject with a future browser editor.
- Read [references/project-config.md](references/project-config.md) when configuring Piper for a work project.
