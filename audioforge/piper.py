"""Piper subprocess adapter."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


class PiperUnavailable(RuntimeError):
    """Raised when Piper or its voice model is not configured."""


def find_piper(explicit: str | None = None) -> str | None:
    candidate = explicit or os.environ.get("AUDIO_FORGE_PIPER")
    if candidate:
        path = Path(candidate).expanduser()
        return str(path) if path.is_file() else None
    return shutil.which("piper")


def find_model(explicit: str | None = None) -> str | None:
    candidate = explicit or os.environ.get("AUDIO_FORGE_PIPER_MODEL")
    if not candidate:
        return None
    path = Path(candidate).expanduser()
    return str(path) if path.is_file() else None


def render_voice(text: str, output: Path, *, piper: str | None = None, model: str | None = None) -> dict[str, str]:
    executable = find_piper(piper)
    voice_model = find_model(model)
    if not executable:
        raise PiperUnavailable("Piper was not found; set AUDIO_FORGE_PIPER or add piper to PATH")
    if not voice_model:
        raise PiperUnavailable("Piper voice model was not found; set AUDIO_FORGE_PIPER_MODEL or pass --model")
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [executable, "--model", voice_model, "--output_file", str(output)]
    completed = subprocess.run(command, input=text, text=True, capture_output=True)
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip() or "unknown Piper error"
        raise RuntimeError(f"Piper failed: {detail}")
    return {"backend": "piper", "executable": executable, "model": voice_model}
