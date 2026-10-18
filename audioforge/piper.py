"""Piper subprocess adapter."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .config import resolve_config_path


class PiperUnavailable(RuntimeError):
    """Raised when Piper or its voice model is not configured."""


def find_piper(config_file: Path | None = None, explicit: str | None = None, configured: str | None = None) -> str | None:
    if explicit:
        path = Path(explicit).expanduser()
        return str(path.resolve()) if path.is_file() else None
    return resolve_config_path(config_file, configured) if config_file else None


def find_model(config_file: Path | None = None, explicit: str | None = None, configured: str | None = None) -> str | None:
    if explicit:
        path = Path(explicit).expanduser()
        return str(path.resolve()) if path.is_file() else None
    return resolve_config_path(config_file, configured) if config_file else None


def render_voice(
    text: str,
    output: Path,
    *,
    config_file: Path | None = None,
    configured_piper: str | None = None,
    configured_model: str | None = None,
    piper: str | None = None,
    model: str | None = None,
) -> dict[str, str]:
    executable = find_piper(config_file, piper, configured_piper)
    voice_model = find_model(config_file, model, configured_model)
    if not executable:
        raise PiperUnavailable("Piper was not found; configure voice.executable in audioforge.config.json")
    if not voice_model:
        raise PiperUnavailable("Piper voice model was not found; configure voice.model in audioforge.config.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [executable, "--model", voice_model, "--output_file", str(output)]
    completed = subprocess.run(command, input=text, text=True, capture_output=True)
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip() or "unknown Piper error"
        raise RuntimeError(f"Piper failed: {detail}")
    return {"backend": "piper", "executable": executable, "model": voice_model}
