"""Local dependency diagnostics."""

from __future__ import annotations

import shutil

from .piper import find_model, find_piper


def status(explicit_piper: str | None = None, explicit_model: str | None = None) -> dict[str, str | bool]:
    piper = find_piper(explicit_piper)
    model = find_model(explicit_model)
    ffmpeg = shutil.which("ffmpeg")
    return {
        "piper": piper or False,
        "piper_model": model or False,
        "ffmpeg": ffmpeg or False,
    }
