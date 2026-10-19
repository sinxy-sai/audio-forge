---
name: audio-forge
description: Create local-first music, sound effects, Piper voice, and CosyVoice zero-shot voice-clone WAV projects with editable parameters, inspectable renders, and a stable AudioProject manifest. Use for local audio assets and prototypes; do not use for Blender workflows, cloud audio APIs, MIDI/DAW projects, or professional mastering.
metadata:
  short-description: Create reproducible music, sound-effect, and Piper voice WAV projects
---

# Audio Forge

Use this skill to turn a music, sound-effect, or voice brief into a small, editable, locally rendered WAV project.

## Operating boundary

- Use the `audioforge` CLI and Python standard library by default. Do not install packages, create a `.venv`, or download samples unless the user explicitly asks for a different workflow.
- Piper handles fixed-voice synthesis. CosyVoice handles local zero-shot cloning when the work project configures its Python executable, source checkout, local model directory, and reference audio. Resolve these from the work project's `audioforge.config.json`; do not download models or use cloud services.
- Speech transcription uses the optional local `faster-whisper` backend when configured under `asr`; keep its model directory in the work project and do not download it automatically.
- Produce an editable `project.json` and source parameters alongside the WAV so the result can be regenerated.
- This skill creates prototypes and game/product assets. Do not describe the output as professional mastering or guaranteed commercial-release audio.
- Do not call external audio-generation services, upload files, or publish output without explicit user instructions.
- Keep the user's requested duration, format, and loop behavior exact when they are provided.
- Treat the caller's current working directory as the workspace root. The skill installation directory is read-only reference material, never an output directory.
- Never create generated audio, source parameters, briefs, README files, or project folders inside the skill installation directory, including its `references/`, `agents/`, or `examples/` folders.

## Workflow

1. Classify the request as **music**, **sound effect**, **voice**, **voice clone**, or **transcription**.
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
7. For Piper voice, use `python -m audioforge generate voice`. For zero-shot voice cloning, use `python -m audioforge generate voice-clone --text "..." --config audioforge.config.json --output <project>`. Pair the reference WAV with its same-stem `.lab` transcript; the `.lab` is the reference prompt and `--text` is the new text to synthesize. Use `python -m audioforge clone-candidates --root <audio-folder>` to inspect references. Keep the CosyVoice Python runtime isolated from the Audio Forge Python environment. If the model is missing, report its exact path and leave the AudioProject brief and parameters.
8. Inspect the actual output with `python -m audioforge inspect`. Report duration, sample rate, bit depth, channels, peak level, and clipping count. If clipping is present, lower the gain and render again unless the user explicitly requested a clipped/lo-fi effect.
9. For transcription, write `analysis/transcript.json` and `analysis/transcript.txt` in the work project, and report the language, segments, model, and output paths.
10. Report absolute paths to the project, WAV, parameters, and transcript outputs, plus the checks that were run. Mention any defaults or limitations that affected the result.

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
- Read [references/project-protocol.md](references/project-protocol.md) when a task needs to exchange an AudioProject with a future browser editor.
- Read [references/project-config.md](references/project-config.md) when configuring Piper for a work project.
- Read [references/voice-model-selection.md](references/voice-model-selection.md) when choosing a local voice, voice-cloning, or speech-recognition model.
- Use `python -m audioforge transcribe` for a configured local faster-whisper transcription task.
