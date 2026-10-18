"""Command-line interface for Audio Forge."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from .doctor import status
from .piper import PiperUnavailable, render_voice
from .procedural import render_music, render_sfx
from .project import write_project, write_source_json
from .wav import inspect_pcm


def _slug(value: str) -> str:
    result = "".join(char.lower() if char.isalnum() else "-" for char in value).strip("-")
    return result or "audio-project"


def _project_root(output: str, title: str) -> Path:
    return Path(output).expanduser().resolve()


def _print_report(report: dict[str, object]) -> None:
    for key, value in report.items():
        print(f"{key}: {value}")


def command_doctor(args: argparse.Namespace) -> int:
    report = status(args.piper, args.model)
    for key, value in report.items():
        print(f"{key}: {value}")
    return 0


def command_generate(args: argparse.Namespace) -> int:
    root = _project_root(args.output, args.title or args.kind)
    render_path = root / "renders" / f"{_slug(args.title or args.kind)}.wav"
    if args.kind == "music":
        metadata = render_music(render_path, args.duration, args.sample_rate, args.seed, args.tempo)
        backend = {"name": "procedural", "mode": "music", "version": "1"}
        inputs = {"brief": args.brief, "duration": args.duration, "tempo": args.tempo, "seed": args.seed}
        track = {"id": "music-main", "file": "renders/" + render_path.name, "start": 0, "gain_db": 0, "pan": 0}
        source = {"kind": "music", **inputs, **metadata}
    elif args.kind == "sfx":
        metadata = render_sfx(render_path, args.brief, args.duration, args.sample_rate, args.seed)
        backend = {"name": "procedural", "mode": "sfx", "version": "1"}
        inputs = {"brief": args.brief, "duration": args.duration, "seed": args.seed}
        track = {"id": "sfx-main", "file": "renders/" + render_path.name, "start": 0, "gain_db": 0, "pan": 0}
        source = {"kind": "sfx", **inputs, **metadata}
    else:
        try:
            metadata = render_voice(args.text, render_path, piper=args.piper, model=args.model)
        except (PiperUnavailable, RuntimeError) as error:
            print(f"error: {error}", file=sys.stderr)
            return 2
        backend = {"name": "piper", **metadata}
        inputs = {"text": args.text, "model": args.model}
        track = {"id": "voice-main", "file": "renders/" + render_path.name, "start": 0, "gain_db": 0, "pan": 0}
        source = {"kind": "voice", **inputs, **metadata}
    write_project(
        root,
        title=args.title or _slug(args.brief if args.kind != "voice" else args.text),
        kind=args.kind,
        backend=backend,
        inputs=inputs,
        tracks=[track],
        outputs=[render_path],
        brief=args.brief if args.kind != "voice" else args.text,
        extra={"analysis": metadata},
    )
    write_source_json(root, "parameters.json", source)
    print(f"project: {root}")
    print(f"render: {render_path}")
    _print_report(inspect_pcm(render_path))
    return 0


def command_inspect(args: argparse.Namespace) -> int:
    report = inspect_pcm(Path(args.path).expanduser().resolve())
    _print_report(report)
    if args.fail_on_clip and report["clipped_samples"]:
        return 1
    return 0


def command_export(args: argparse.Namespace) -> int:
    project = Path(args.project).expanduser().resolve()
    manifest = json.loads((project / "project.json").read_text(encoding="utf-8"))
    if not manifest.get("outputs"):
        print("error: project has no outputs", file=sys.stderr)
        return 2
    source = project / manifest["outputs"][0]
    target = source.with_suffix("." + args.format)
    executable = args.ffmpeg or "ffmpeg"
    command = [executable, "-y", "-i", str(source), str(target)]
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode:
        print(completed.stderr.strip() or "ffmpeg failed", file=sys.stderr)
        return 2
    print(f"export: {target}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="audio-forge")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="report local tool availability")
    doctor.add_argument("--piper")
    doctor.add_argument("--model")
    doctor.set_defaults(handler=command_doctor)

    generate = subparsers.add_parser("generate", help="generate an audio project")
    generate_sub = generate.add_subparsers(dest="kind", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--output", required=True)
    common.add_argument("--title")
    common.add_argument("--duration", type=float, default=8.0)
    common.add_argument("--sample-rate", type=int, default=44100)
    common.add_argument("--seed", type=int, default=0)
    music = generate_sub.add_parser("music", parents=[common])
    music.add_argument("--brief", required=True)
    music.add_argument("--tempo", type=int, default=100)
    music.set_defaults(handler=command_generate)
    sfx = generate_sub.add_parser("sfx", parents=[common])
    sfx.add_argument("--brief", required=True)
    sfx.set_defaults(duration=0.5)
    sfx.set_defaults(handler=command_generate)
    voice = generate_sub.add_parser("voice", parents=[common])
    voice.add_argument("--text", required=True)
    voice.add_argument("--piper")
    voice.add_argument("--model")
    voice.set_defaults(handler=command_generate)

    inspect = subparsers.add_parser("inspect", help="inspect a PCM WAV")
    inspect.add_argument("path")
    inspect.add_argument("--fail-on-clip", action="store_true")
    inspect.set_defaults(handler=command_inspect)

    export = subparsers.add_parser("export", help="convert the first project output with FFmpeg")
    export.add_argument("project")
    export.add_argument("--format", choices=("ogg", "mp3", "wav"), required=True)
    export.add_argument("--ffmpeg")
    export.set_defaults(handler=command_export)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.handler(args)
