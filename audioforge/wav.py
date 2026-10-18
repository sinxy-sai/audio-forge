"""Small PCM WAV helpers shared by generators and inspectors."""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path
from typing import Iterable


def write_pcm16(path: Path, samples: Iterable[float] | Iterable[tuple[float, float]], sample_rate: int, channels: int) -> None:
    if channels not in (1, 2):
        raise ValueError("channels must be 1 or 2")
    path.parent.mkdir(parents=True, exist_ok=True)
    frames = bytearray()
    if channels == 1:
        for sample in samples:  # type: ignore[assignment]
            value = max(-1.0, min(1.0, float(sample)))
            frames += struct.pack("<h", round(value * 32767))
    else:
        for left, right in samples:  # type: ignore[misc]
            frames += struct.pack(
                "<hh",
                round(max(-1.0, min(1.0, float(left))) * 32767),
                round(max(-1.0, min(1.0, float(right))) * 32767),
            )
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(channels)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(frames)


def inspect_pcm(path: Path) -> dict[str, float | int]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with wave.open(str(path), "rb") as handle:
        channels = handle.getnchannels()
        sample_rate = handle.getframerate()
        sample_width = handle.getsampwidth()
        frames = handle.getnframes()
        raw = handle.readframes(frames)
    if sample_width != 2:
        raise ValueError(f"only 16-bit PCM is supported: {sample_width} bytes")
    count = frames * channels
    values = struct.unpack(f"<{count}h", raw) if raw else ()
    peak = max((abs(value) / 32767.0 for value in values), default=0.0)
    clipped = sum(abs(value) >= 32767 for value in values)
    return {
        "channels": channels,
        "sample_rate": sample_rate,
        "sample_width": sample_width,
        "frames": frames,
        "duration": frames / sample_rate if sample_rate else math.nan,
        "peak": peak,
        "clipped_samples": clipped,
    }
