"""Implement Audio Forge CLI commands."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from .config import ConfigUnavailable, load_asr_config, load_voice_config
from .doctor import status
from .piper import PiperUnavailable, render_voice
from .transcribe import TranscriptionUnavailable, transcribe_audio, write_transcription
from .procedural import render_music, render_sfx
from .project import write_project, write_source_json
from .wav import inspect_pcm


def slug(value: str) -> str:
    result = "".join(char.lower() if char.isalnum() else "-" for char in value).strip("-")
    return result or "audio-project"


def print_report(report: dict[str, object]) -> None:
    for key, value in report.items():
        print(f"{key}: {value}")


def doctor(args) -> int:
    print_report(status(args.config, args.piper, args.model))
    return 0


def generate(args) -> int:
    root = Path(args.output).expanduser().resolve()
    title = args.title or (args.brief if args.kind != "voice" else args.text)
    render_path = root / "renders" / f"{slug(args.title or args.kind)}.wav"

    if args.kind == "music":
        metadata = render_music(render_path, args.duration, args.sample_rate, args.seed, args.tempo)
        backend = {"name": "procedural", "mode": "music", "version": "1"}
        inputs = {"brief": args.brief, "duration": args.duration, "tempo": args.tempo, "seed": args.seed}
        source = {"kind": "music", **inputs, **metadata}
        track_id, brief = "music-main", args.brief
    elif args.kind == "sfx":
        metadata = render_sfx(render_path, args.brief, args.duration, args.sample_rate, args.seed)
        backend = {"name": "procedural", "mode": "sfx", "version": "1"}
        inputs = {"brief": args.brief, "duration": args.duration, "seed": args.seed}
        source = {"kind": "sfx", **inputs, **metadata}
        track_id, brief = "sfx-main", args.brief
    else:
        try:
            voice = load_voice_config(args.config, [Path.cwd(), root], args.piper, args.model)
            metadata = render_voice(args.text, render_path, voice=voice, volume=args.volume)
        except (ConfigUnavailable, PiperUnavailable, RuntimeError, ValueError) as error:
            print(f"error: {error}", file=sys.stderr)
            return 2
        backend = {"name": "piper", **metadata}
        inputs = {"text": args.text, "model": str(voice.model)}
        source = {"kind": "voice", **inputs, **metadata}
        track_id, brief = "voice-main", args.text

    track = {"id": track_id, "file": f"renders/{render_path.name}", "start": 0, "gain_db": 0, "pan": 0}
    write_project(root, title=title, kind=args.kind, backend=backend, inputs=inputs, tracks=[track], outputs=[render_path], brief=brief, extra={"analysis": metadata})
    write_source_json(root, "parameters.json", source)
    print(f"project: {root}")
    print(f"render: {render_path}")
    print_report(inspect_pcm(render_path))
    return 0


def transcribe(args) -> int:
    root = Path(args.output).expanduser().resolve()
    audio = Path(args.audio).expanduser().resolve()
    try:
        asr = load_asr_config(
            args.config,
            [Path.cwd(), root, audio],
            args.model,
            args.device,
            args.compute_type,
        )
        result = transcribe_audio(
            audio,
            asr=asr,
            language=args.language,
            beam_size=args.beam_size,
            vad_filter=not args.no_vad,
        )
        model_path = asr.model
        try:
            result["model"] = model_path.relative_to(asr.config_file.parent).as_posix()
        except ValueError:
            result["model"] = model_path.as_posix()
        json_path, text_path = write_transcription(root, audio, result)
        manifest_path = root / "project.json"
        if manifest_path.is_file():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest.setdefault("analysis", {})["transcription"] = {
                "json": "analysis/transcript.json",
                "text": "analysis/transcript.txt",
                "backend": result["backend"],
                "language": result["language"],
            }
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (ConfigUnavailable, TranscriptionUnavailable, OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(f"project: {root}")
    print(f"audio: {audio}")
    print(f"transcript_json: {json_path}")
    print(f"transcript_text: {text_path}")
    print(f"language: {result['language']}")
    print(f"language_probability: {result['language_probability']}")
    for segment in result["segments"]:
        print(f"[{segment['start']:.2f}-{segment['end']:.2f}] {segment['text']}")
    return 0


def inspect(args) -> int:
    report = inspect_pcm(Path(args.path).expanduser().resolve())
    print_report(report)
    return 1 if args.fail_on_clip and report["clipped_samples"] else 0


def export(args) -> int:
    project = Path(args.project).expanduser().resolve()
    manifest = json.loads((project / "project.json").read_text(encoding="utf-8"))
    if not manifest.get("outputs"):
        print("error: project has no outputs", file=sys.stderr)
        return 2
    source = project / manifest["outputs"][0]
    target = source.with_suffix("." + args.format)
    completed = subprocess.run([args.ffmpeg or "ffmpeg", "-y", "-i", str(source), str(target)], capture_output=True, text=True)
    if completed.returncode:
        print(completed.stderr.strip() or "ffmpeg failed", file=sys.stderr)
        return 2
    print(f"export: {target}")
    return 0

