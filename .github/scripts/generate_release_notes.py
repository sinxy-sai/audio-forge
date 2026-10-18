"""Generate a release note from a tag and its direct commit history."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / ".github" / "release-notes-template.md"
COMMIT_RE = re.compile(r"^(?P<type>[a-z]+)(?:\((?P<scope>[^)]+)\))?!?:\s+(?P<subject>.+)$")


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def previous_tag(tag: str) -> str | None:
    tags = git("tag", "--sort=-version:refname").splitlines()
    for candidate in tags:
        if candidate == tag or not candidate.startswith("v"):
            continue
        if subprocess.run(
            ["git", "merge-base", "--is-ancestor", candidate, tag], cwd=ROOT
        ).returncode == 0:
            return candidate
    return None


def commits(tag: str, previous: str | None) -> list[tuple[str, str]]:
    revision = f"{previous}..{tag}" if previous else f"{tag}"
    output = git("log", "--first-parent", "--format=%H%x09%s", revision)
    return [tuple(line.split("\t", 1)) for line in output.splitlines() if "\t" in line]


def classify(subject: str) -> tuple[str, str]:
    match = COMMIT_RE.match(subject)
    if not match:
        return "maintenance", subject
    commit_type = match.group("type")
    label = {
        "feat": "highlights",
        "fix": "fixes",
        "perf": "highlights",
        "docs": "maintenance",
        "refactor": "maintenance",
        "test": "maintenance",
        "chore": "maintenance",
        "build": "maintenance",
        "ci": "maintenance",
    }.get(commit_type, "maintenance")
    scope = match.group("scope")
    subject_text = match.group("subject")
    if scope:
        subject_text = f"**{scope}:** {subject_text}"
    return label, subject_text


def bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- No changes in this category."


def render(tag: str, previous: str | None, entries: list[tuple[str, str]]) -> str:
    groups = {"highlights": [], "fixes": [], "maintenance": []}
    for commit_hash, subject in entries:
        group, text = classify(subject)
        groups[group].append(f"{text} (`{commit_hash[:8]}`)")
    full = "\n".join(f"- `{commit_hash[:8]}` {subject}" for commit_hash, subject in entries)
    if not full:
        full = "- No direct commits found in this range."
    previous_text = previous or "the beginning of the repository"
    if not TEMPLATE.is_file():
        raise FileNotFoundError(f"release note template not found: {TEMPLATE}")
    template = TEMPLATE.read_text(encoding="utf-8")
    replacements = {
        "{{VERSION}}": tag,
        "{{HIGHLIGHTS}}": bullets(groups["highlights"]),
        "{{FIXES}}": bullets(groups["fixes"]),
        "{{MAINTENANCE}}": bullets(groups["maintenance"]),
        "{{FULL_CHANGELOG}}": f"Changes since {previous_text}:\n\n{full}",
    }
    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)
    return template


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    previous = previous_tag(args.tag)
    content = render(args.tag, previous, commits(args.tag, previous))
    if args.output:
        args.output.write_text(content, encoding="utf-8", newline="\n")
    else:
        print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
