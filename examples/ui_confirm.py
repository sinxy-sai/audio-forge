"""Create a short two-tone UI confirmation sound with no third-party packages."""

from __future__ import annotations

import argparse
import math
import struct
import wave
from pathlib import Path


SAMPLE_RATE = 44100


def render(output: Path) -> None:
    notes = ((0.0, 0.18, 523.25), (0.16, 0.32, 783.99))
    duration = 0.52
    frames = int(duration * SAMPLE_RATE)
    output.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        data = bytearray()
        for index in range(frames):
            t = index / SAMPLE_RATE
            value = 0.0
            for start, note_duration, frequency in notes:
                local = t - start
                if 0 <= local < note_duration:
                    attack = min(1.0, local / 0.008)
                    release = max(0.0, 1.0 - local / note_duration) ** 2
                    value += 0.28 * attack * release * math.sin(2 * math.pi * frequency * local)
            encoded = int(max(-1.0, min(1.0, value)) * 32767)
            data += struct.pack("<h", encoded)
        wav_file.writeframes(data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    render(args.output)
    print(f"Wrote {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
