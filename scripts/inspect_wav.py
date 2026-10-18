"""Inspect a 16-bit PCM WAV using Audio Forge's shared implementation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from audioforge.wav import inspect_pcm


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--fail-on-clip", action="store_true")
    args = parser.parse_args()
    try:
        report = inspect_pcm(args.path)
    except (FileNotFoundError, OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(f"path: {args.path.resolve()}")
    print(f"channels: {report['channels']}")
    print(f"sample_rate_hz: {report['sample_rate']}")
    print(f"sample_width_bytes: {report['sample_width']}")
    print(f"frames: {report['frames']}")
    print(f"duration_seconds: {report['duration']:.6f}")
    print(f"peak_normalized: {report['peak']:.6f}")
    print(f"clipped_samples: {report['clipped_samples']}")
    return 1 if args.fail_on_clip and report["clipped_samples"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
