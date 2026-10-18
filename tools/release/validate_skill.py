"""Validate the tracked shape of the Audio Forge skill before a release."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REQUIRED_FILES = (
    Path("SKILL.md"),
    Path("agents/openai.yaml"),
    Path("scripts/synth_tone.py"),
    Path("scripts/inspect_wav.py"),
    Path("references/presets.md"),
    Path("CHANGELOG.md"),
    Path("SECURITY.md"),
    Path("CODE_OF_CONDUCT.md"),
)
VERSION_PATTERN = re.compile(r"^v\d+\.\d+\.\d+(?:-(?:alpha|beta|rc)\.\d+)?$")


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, check=True, capture_output=True, text=True
    )
    return [line for line in result.stdout.splitlines() if line]


def validate() -> list[str]:
    problems: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            problems.append(f"missing required file: {relative.as_posix()}")

    skill_path = ROOT / "SKILL.md"
    if skill_path.is_file():
        text = skill_path.read_text(encoding="utf-8")
        if not text.startswith("---\n") or "\n---\n" not in text[4:]:
            problems.append("SKILL.md is missing YAML frontmatter")
        if not re.search(r"^name:\s*audio-forge\s*$", text, re.MULTILINE):
            problems.append("SKILL.md frontmatter must name audio-forge")
        if not re.search(r"^description:\s*\S", text, re.MULTILINE):
            problems.append("SKILL.md frontmatter needs a description")
        if re.search(r"\b(?:TODO|TBD|\[TODO)", text, re.IGNORECASE):
            problems.append("SKILL.md contains an unfinished placeholder")

    gitignore = ROOT / ".gitignore"
    if not gitignore.is_file() or "docs/private/" not in gitignore.read_text(encoding="utf-8"):
        problems.append(".gitignore must keep docs/private/ out of public releases")

    forbidden = []
    for name in tracked_files():
        normalized = name.replace("\\", "/")
        if normalized.startswith("docs/private/"):
            forbidden.append(name)
        if normalized.endswith((".wav", ".mp3", ".flac")):
            forbidden.append(name)
        if "__pycache__/" in normalized:
            forbidden.append(name)
    for name in sorted(set(forbidden)):
        problems.append(f"generated or private file is tracked: {name}")

    return problems


def main() -> int:
    if len(sys.argv) > 1 and not VERSION_PATTERN.fullmatch(sys.argv[1]):
        print(f"error: unsupported release tag: {sys.argv[1]}", file=sys.stderr)
        return 2
    problems = validate()
    if problems:
        for problem in problems:
            print(f"error: {problem}", file=sys.stderr)
        return 1
    print("Audio Forge skill validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
