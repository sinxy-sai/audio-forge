"""Local dependency diagnostics."""

from __future__ import annotations

import shutil
from pathlib import Path

from .config import ConfigUnavailable, load_config
from .piper import find_model, find_piper


def status(config: str | None = None, explicit_piper: str | None = None, explicit_model: str | None = None) -> dict[str, str | bool]:
    try:
        config_file, data = load_config(config)
        voice = data.get("voice", {})
        piper = find_piper(config_file, explicit_piper, voice.get("executable"))
        model = find_model(config_file, explicit_model, voice.get("model"))
        config_status: str | bool = str(config_file)
    except ConfigUnavailable:
        piper = find_piper(None, explicit_piper)
        model = find_model(None, explicit_model)
        config_status = False
    ffmpeg = shutil.which("ffmpeg")
    return {
        "config": config_status,
        "piper": piper or False,
        "piper_model": model or False,
        "ffmpeg": ffmpeg or False,
    }
