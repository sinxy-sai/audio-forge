"""Piper voice backend."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .config import VoiceConfig


class PiperUnavailable(RuntimeError):
    """Raised when Piper cannot render a voice request."""


def _project_path(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()


def render_voice(text: str, output: Path, *, voice: VoiceConfig, volume: float = 0.95) -> dict[str, str]:
    if not 0 < volume <= 1:
        raise ValueError("volume must be in the range (0, 1]")
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [str(voice.executable), "--model", str(voice.model), "--output_file", str(output), "--volume", str(volume)]
    completed = subprocess.run(command, input=text, text=True, capture_output=True)
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip() or "unknown Piper error"
        raise PiperUnavailable(f"Piper failed: {detail}")
    return {
        "backend": "piper",
        "config": voice.config_file.name,
        "executable": _project_path(voice.executable, voice.config_file.parent),
        "model": _project_path(voice.model, voice.config_file.parent),
        "volume": str(volume),
    }
