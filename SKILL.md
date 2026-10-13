---
name: audio-forge
description: Create short music and sound-effect WAV files from a brief using reproducible, editable Python synthesis. Use when the user wants a local audio prototype, UI sound, game sound, loop, or short background cue; do not use for MIDI, DAW projects, external audio models, or professional mastering.
metadata:
  short-description: Create reproducible music and sound-effect WAV prototypes
---

# Audio Forge

Use this skill to turn a music or sound-effect brief into a small, editable, locally rendered WAV project.

## Operating boundary

- Use Python's standard library by default. Do not install packages or download samples unless the user explicitly asks for a different workflow.
- Produce a source script as well as the WAV so the result can be edited and regenerated.
- This skill creates prototypes and game/product assets. Do not describe the output as professional mastering or guaranteed commercial-release audio.
- Do not call external audio-generation services, upload files, or publish output without explicit user instructions.
- Keep the user's requested duration, format, and loop behavior exact when they are provided.
- Treat the caller's current working directory as the workspace root. The skill installation directory is read-only reference material, never an output directory.
- Never create generated audio, source scripts, briefs, README files, or project folders inside the skill installation directory, including its `scripts/`, `references/`, `agents/`, or `examples/` folders.

## Workflow

1. Classify the request as **music** or **sound effect**.
2. Extract the brief: purpose, duration, mood, style, pitch or tempo, main timbres, loop requirement, sample rate, channel count, and output location.
3. Ask only for missing details that materially affect the result. Otherwise use these defaults and state them: 44,100 Hz, 16-bit PCM WAV, stereo for music, mono for short effects, and a short fade-in/fade-out to prevent clicks.
4. Resolve the output root before creating files. If the user gives an output path, resolve a relative path from the caller's current working directory. Otherwise create a project directory named from the user's requested asset under the caller's current working directory, for example `bundle/jump-effect/`. State the absolute output root before rendering.

   ```text
   <caller-current-working-directory>/<project-slug>/
   ```

   Do not use the skill directory as a fallback when the requested name or output path is missing; ask for the missing project name or use a clearly stated slug under the caller's current working directory.

5. Create the project with:

   ```text
   project/
   |-- brief.md
   |-- source/
   |   `-- *.py
   |-- renders/
   |   `-- *.wav
   `-- README.md
   ```

   If the user only requests a quick preview, a WAV and source script may be placed directly in the requested folder.

6. Build the sound from explicit layers such as oscillators, envelopes, noise bursts, pulses, pitch glides, stereo pan, and short delays. Keep parameters near the top of the generated script.
7. Render the WAV by running the source script. Prefer the bundled `scripts/synth_tone.py` as a small reference or smoke-test generator; adapt it rather than hiding the whole composition in opaque code. The generated script must live under the resolved output root, not beside the skill instructions.
8. Inspect the actual output with `scripts/inspect_wav.py`. Report duration, sample rate, bit depth, channels, peak level, and clipping count. If clipping is present, lower the gain and render again unless the user explicitly requested a clipped/lo-fi effect.
9. Report absolute paths to the WAV and source, plus the checks that were run. Mention any defaults or limitations that affected the result.

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
