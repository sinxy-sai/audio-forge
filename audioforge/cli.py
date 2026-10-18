"""Argument parser for the Audio Forge CLI."""

from __future__ import annotations

import argparse

from .commands import doctor, export, generate, inspect


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="audio-forge")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor_parser = subparsers.add_parser("doctor", help="report local tool availability")
    doctor_parser.add_argument("--config")
    doctor_parser.add_argument("--piper")
    doctor_parser.add_argument("--model")
    doctor_parser.set_defaults(handler=doctor)

    generate_parser = subparsers.add_parser("generate", help="generate an audio project")
    kinds = generate_parser.add_subparsers(dest="kind", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--output", required=True)
    common.add_argument("--title")
    common.add_argument("--duration", type=float, default=8.0)
    common.add_argument("--sample-rate", type=int, default=44100)
    common.add_argument("--seed", type=int, default=0)

    music = kinds.add_parser("music", parents=[common])
    music.add_argument("--brief", required=True)
    music.add_argument("--tempo", type=int, default=100)
    music.set_defaults(handler=generate)

    sfx = kinds.add_parser("sfx", parents=[common])
    sfx.add_argument("--brief", required=True)
    sfx.set_defaults(duration=0.5, handler=generate)

    voice = kinds.add_parser("voice", parents=[common])
    voice.add_argument("--text", required=True)
    voice.add_argument("--config")
    voice.add_argument("--piper", help="one-off executable override")
    voice.add_argument("--model", help="one-off model override")
    voice.add_argument("--volume", type=float, default=0.95)
    voice.set_defaults(handler=generate)

    inspect_parser = subparsers.add_parser("inspect", help="inspect a PCM WAV")
    inspect_parser.add_argument("path")
    inspect_parser.add_argument("--fail-on-clip", action="store_true")
    inspect_parser.set_defaults(handler=inspect)

    export_parser = subparsers.add_parser("export", help="convert the first project output with FFmpeg")
    export_parser.add_argument("project")
    export_parser.add_argument("--format", choices=("ogg", "mp3", "wav"), required=True)
    export_parser.add_argument("--ffmpeg")
    export_parser.set_defaults(handler=export)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.handler(args)
