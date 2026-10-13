"""Generate a dependency-free WAV tone with a fade envelope."""

from __future__ import annotations

import argparse
import math
import struct
import wave
from pathlib import Path


def render(output: Path, frequency: float, duration: float, sample_rate: int, channels: int, amplitude: float) -> None:
    if frequency <= 0 or duration <= 0:
        raise ValueError("frequency and duration must be positive")
    if sample_rate < 8000:
        raise ValueError("sample_rate must be at least 8000 Hz")
    if channels not in (1, 2):
        raise ValueError("channels must be 1 or 2")
    if not 0 < amplitude <= 1:
        raise ValueError("amplitude must be in the range (0, 1]")

    frames = int(round(duration * sample_rate))
    fade = max(1, min(int(0.012 * sample_rate), frames // 2))
    output.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output), "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        data = bytearray()
        for index in range(frames):
            t = index / sample_rate
            envelope = 1.0
            if index < fade:
                envelope = index / fade
            elif index >= frames - fade:
                envelope = (frames - index - 1) / fade
            sample = max(-1.0, min(1.0, amplitude * envelope * math.sin(2 * math.pi * frequency * t)))
            encoded = int(round(sample * 32767))
            data += struct.pack("<h", encoded) if channels == 1 else struct.pack("<hh", encoded, encoded)
        wav_file.writeframes(data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="output WAV path")
    parser.add_argument("--frequency", type=float, default=440.0)
    parser.add_argument("--duration", type=float, default=0.5)
    parser.add_argument("--sample-rate", type=int, default=44100)
    parser.add_argument("--channels", type=int, choices=(1, 2), default=1)
    parser.add_argument("--amplitude", type=float, default=0.6)
    args = parser.parse_args()
    render(args.output, args.frequency, args.duration, args.sample_rate, args.channels, args.amplitude)
    print(f"Wrote {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
