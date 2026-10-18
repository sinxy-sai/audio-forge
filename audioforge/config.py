"""Project-local Audio Forge configuration discovery."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ConfigUnavailable(RuntimeError):
    """Raised when a project-local config cannot be loaded."""


def find_config(explicit: str | None = None, search_paths: list[Path] | None = None) -> Path | None:
    if explicit:
        path = Path(explicit).expanduser().resolve()
        return path if path.is_file() else None
    starts = search_paths or [Path.cwd()]
    for start in starts:
        current = start.expanduser().resolve()
        if current.is_file():
            current = current.parent
        for directory in (current, *current.parents):
            candidate = directory / "audioforge.config.json"
            if candidate.is_file():
                return candidate
    return None


def load_config(explicit: str | None = None, search_paths: list[Path] | None = None) -> tuple[Path, dict[str, Any]]:
    path = find_config(explicit, search_paths)
    if not path:
        raise ConfigUnavailable("audioforge.config.json was not found in the work project")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ConfigUnavailable(f"could not read {path}: {error}") from error
    if not isinstance(data, dict):
        raise ConfigUnavailable(f"configuration must be a JSON object: {path}")
    return path, data


def resolve_config_path(config_file: Path, value: str | None) -> str | None:
    if not value:
        return None
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = config_file.parent / path
    return str(path.resolve()) if path.is_file() else None

