"""Inspect a PCM WAV and report format, duration, peak, and clipping."""

from __future__ import annotations

import argparse
import math
import struct
import sys
import wave
from pathlib import Path


def inspect(path: Path) -> dict[str, float | int]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with wave.open(str(path), "rb") as wav_file:
        channels = wav_file.getnchannels()
        sample_rate = wav_file.getframerate()
        sample_width = wav_file.getsampwidth()
        frames = wav_file.getnframes()
        raw = wav_file.readframes(frames)
    if sample_width not in (1, 2, 3, 4):
        raise ValueError(f"unsupported PCM sample width: {sample_width} bytes")
    total_samples = frames * channels
    if sample_width == 2:
        values = struct.unpack(f"<{total_samples}h", raw) if raw else ()
        peak = max((abs(value) / 32767.0 for value in values), default=0.0)
        clipped = sum(abs(value) >= 32767 for value in values)
    elif sample_width == 1:
        values = raw
        peak = max((abs(value - 128) / 127.0 for value in values), default=0.0)
        clipped = sum(value in (0, 255) for value in values)
    else:
        peak = math.nan
        clipped = 0
    return {
        "channels": channels,
        "sample_rate": sample_rate,
        "sample_width": sample_width,
        "frames": frames,
        "duration": frames / sample_rate if sample_rate else math.nan,
        "peak": peak,
        "clipped_samples": clipped,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--fail-on-clip", action="store_true")
    args = parser.parse_args()
    try:
        report = inspect(args.path)
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
