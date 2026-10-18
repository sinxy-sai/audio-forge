"""Project-local Audio Forge configuration."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ConfigUnavailable(RuntimeError):
    """Raised when a work-project configuration cannot be loaded."""


@dataclass(frozen=True)
class VoiceConfig:
    config_file: Path
    executable: Path
    model: Path


@dataclass(frozen=True)
class AsrConfig:
    config_file: Path
    backend: str
    model: Path
    device: str
    compute_type: str


def find_config(explicit: str | None = None, search_paths: list[Path] | None = None) -> Path | None:
    if explicit:
        candidate = Path(explicit).expanduser().resolve()
        return candidate if candidate.is_file() else None
    for start in search_paths or [Path.cwd()]:
        current = start.expanduser().resolve()
        current = current.parent if current.is_file() else current
        for directory in (current, *current.parents):
            candidate = directory / "audioforge.config.json"
            if candidate.is_file():
                return candidate
    return None


def _load(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ConfigUnavailable(f"could not read {path}: {error}") from error
    if not isinstance(data, dict):
        raise ConfigUnavailable(f"configuration must be a JSON object: {path}")
    return data


def _resolve(config_file: Path, value: str | None, label: str) -> Path:
    if not value:
        raise ConfigUnavailable(f"voice.{label} is missing in {config_file}")
    path = Path(value).expanduser()
    path = path if path.is_absolute() else config_file.parent / path
    path = path.resolve()
    if not path.is_file():
        raise ConfigUnavailable(f"voice.{label} does not exist: {path}")
    return path


def load_voice_config(
    explicit: str | None = None,
    search_paths: list[Path] | None = None,
    executable_override: str | None = None,
    model_override: str | None = None,
) -> VoiceConfig:
    config_file = find_config(explicit, search_paths)
    if not config_file:
        if executable_override and model_override:
            executable = Path(executable_override).expanduser().resolve()
            model = Path(model_override).expanduser().resolve()
            if not executable.is_file() or not model.is_file():
                raise ConfigUnavailable("one-off Piper executable or model override does not exist")
            return VoiceConfig(config_file=Path.cwd(), executable=executable, model=model)
        raise ConfigUnavailable("audioforge.config.json was not found in the work project")
    voice = _load(config_file).get("voice")
    if not isinstance(voice, dict):
        raise ConfigUnavailable(f"voice configuration is missing in {config_file}")
    executable = _resolve(config_file, executable_override or voice.get("executable"), "executable")
    model = _resolve(config_file, model_override or voice.get("model"), "model")
    return VoiceConfig(config_file=config_file, executable=executable, model=model)



def load_asr_config(
    explicit: str | None = None,
    search_paths: list[Path] | None = None,
    model_override: str | None = None,
    device_override: str | None = None,
    compute_type_override: str | None = None,
) -> AsrConfig:
    config_file = find_config(explicit, search_paths)
    if not config_file:
        if not model_override:
            raise ConfigUnavailable("audioforge.config.json was not found in the work project")
        model = Path(model_override).expanduser().resolve()
        if not model.is_dir():
            raise ConfigUnavailable(f"ASR model directory does not exist: {model}")
        return AsrConfig(
            config_file=Path.cwd(),
            backend="faster-whisper",
            model=model,
            device=device_override or "cpu",
            compute_type=compute_type_override or "int8",
        )

    data = _load(config_file)
    asr = data.get("asr")
    if not isinstance(asr, dict):
        raise ConfigUnavailable(f"ASR configuration is missing in {config_file}")
    backend = str(asr.get("backend", "faster-whisper"))
    if backend != "faster-whisper":
        raise ConfigUnavailable(f"unsupported ASR backend: {backend}")
    model_value = model_override or asr.get("model")
    if not model_value:
        raise ConfigUnavailable(f"asr.model is missing in {config_file}")
    model = Path(str(model_value)).expanduser()
    model = model if model.is_absolute() else config_file.parent / model
    model = model.resolve()
    if not model.is_dir():
        raise ConfigUnavailable(f"asr.model does not exist: {model}")
    return AsrConfig(
        config_file=config_file,
        backend=backend,
        model=model,
        device=device_override or str(asr.get("device", "cpu")),
        compute_type=compute_type_override or str(asr.get("compute_type", "int8")),
    )
