"""Local dependency diagnostics."""

from __future__ import annotations

import shutil

from .config import ConfigUnavailable, load_voice_config


def status(config: str | None = None, piper: str | None = None, model: str | None = None) -> dict[str, str | bool]:
    try:
        voice = load_voice_config(config, executable_override=piper, model_override=model)
        report: dict[str, str | bool] = {
            "config": str(voice.config_file),
            "piper": str(voice.executable),
            "piper_model": str(voice.model),
        }
    except ConfigUnavailable as error:
        report = {"config": False, "piper": False, "piper_model": False, "error": str(error)}
    report["ffmpeg"] = shutil.which("ffmpeg") or False
    return report
