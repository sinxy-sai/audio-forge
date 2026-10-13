# Audio Forge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `audio-forge` skill as a dependency-free workflow for creating and inspecting editable local music and sound-effect WAV prototypes.

**Architecture:** The skill entrypoint routes brief-driven requests into music or sound-effect mode. Two standard-library scripts provide a minimal WAV generator and an output inspector; reference presets guide decisions without restricting generated compositions.

**Tech Stack:** Markdown, YAML, Python 3 standard library, RIFF/WAV PCM.

**Spec:** `docs/superpowers/specs/2026-10-13-audio-forge-design.md`

## Global Constraints

- Do not install packages or download samples for the default workflow.
- Preserve editable Python source alongside every generated WAV.
- Report actual output properties after rendering.
- Keep MIDI, DAW, external model, publishing, and professional mastering outside v1.

---

### Task 1: Create the skill entrypoint and routing metadata

**Files:** `SKILL.md`, `agents/openai.yaml`

- [x] Define discriminating activation text for local brief-to-WAV work.
- [x] Document brief extraction, synthesis, inspection, clipping response, and reporting.
- [x] Add display name, short description, and default prompt.

### Task 2: Add reusable WAV scripts

**Files:** `scripts/synth_tone.py`, `scripts/inspect_wav.py`

- [x] Implement a standard-library tone renderer with fades and configurable format.
- [x] Implement metadata, peak, and clipping inspection with nonzero error modes.

### Task 3: Add presets and validate

**Files:** `references/presets.md`

- [x] Document starting presets for music, UI click, confirmation, warning, impact, rising cue, and whoosh.
- [x] Run the official skill validator.
- [x] Render and inspect a smoke-test WAV with zero clipping.
