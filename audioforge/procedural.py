"""Dependency-light procedural music and sound-effect rendering."""

from __future__ import annotations

import math
import random
from pathlib import Path
from typing import Any

from .wav import write_pcm16


def _fade(local: float, duration: float, attack: float = 0.008) -> float:
    if local < 0 or local >= duration:
        return 0.0
    attack_gain = min(1.0, local / attack) if attack else 1.0
    release_gain = min(1.0, max(0.0, (duration - local) / max(attack, duration * 0.22)))
    return attack_gain * release_gain


def render_music(path: Path, duration: float = 8.0, sample_rate: int = 44100, seed: int = 0, tempo: int = 100) -> dict[str, Any]:
    if duration <= 0:
        raise ValueError("duration must be positive")
    rng = random.Random(seed)
    beat = 60.0 / tempo
    root = rng.choice((146.83, 164.81, 196.0, 220.0))
    chords = ((1.0, 1.25, 1.5), (1.0, 1.2, 1.5), (0.89, 1.12, 1.33), (0.75, 0.94, 1.19))
    frames = int(round(duration * sample_rate))
    rendered: list[tuple[float, float]] = []
    for index in range(frames):
        t = index / sample_rate
        bar = int(t / (beat * 4))
        chord = chords[bar % len(chords)]
        pad = sum(math.sin(2 * math.pi * root * ratio * t) for ratio in chord) / len(chord)
        pulse = math.sin(2 * math.pi * root * 0.5 * t) * (0.5 + 0.5 * math.sin(math.pi * (t % beat) / beat))
        motif_note = (root * (1.0, 1.12, 1.25, 1.5)[int((t % (beat * 2)) / (beat / 2)) % 4])
        motif = math.sin(2 * math.pi * motif_note * t) * _fade(t % (beat / 2), beat / 2, 0.01) * 0.35
        value = 0.22 * pad + 0.12 * pulse + motif
        pan = 0.08 * math.sin(2 * math.pi * t / max(duration, 1.0))
        rendered.append((value * (1.0 - pan), value * (1.0 + pan)))
    write_pcm16(path, rendered, sample_rate, 2)
    return {"duration": duration, "sample_rate": sample_rate, "channels": 2, "seed": seed, "tempo": tempo, "root_hz": root}


def render_sfx(path: Path, brief: str, duration: float = 0.5, sample_rate: int = 44100, seed: int = 0) -> dict[str, Any]:
    if duration <= 0:
        raise ValueError("duration must be positive")
    words = brief.lower()
    kind = "confirm" if any(word in words for word in ("confirm", "确认", "success", "完成")) else "click" if any(word in words for word in ("click", "点击")) else "warning" if any(word in words for word in ("warning", "警告")) else "impact" if any(word in words for word in ("impact", "冲击", "爆炸")) else "whoosh" if any(word in words for word in ("whoosh", "sweep", "上升")) else "tone"
    rng = random.Random(seed)
    frames = int(round(duration * sample_rate))
    rendered: list[float] = []
    for index in range(frames):
        t = index / sample_rate
        value = 0.0
        if kind == "confirm":
            for start, length, frequency in ((0.0, duration * 0.42, 520.0), (duration * 0.34, duration * 0.58, 780.0)):
                value += 0.32 * _fade(t - start, length) * math.sin(2 * math.pi * frequency * (t - start))
        elif kind == "click":
            value = 0.58 * math.exp(-45 * t) * math.sin(2 * math.pi * 1500 * t)
        elif kind == "warning":
            frequency = 420.0 if int(t / max(duration / 3, 0.001)) % 2 == 0 else 620.0
            value = 0.34 * _fade(t % (duration / 3), duration / 3, 0.003) * math.sin(2 * math.pi * frequency * t)
        elif kind == "impact":
            value = 0.5 * math.exp(-9 * t) * math.sin(2 * math.pi * (120 - 70 * min(1.0, t / duration)) * t)
            value += 0.16 * math.exp(-32 * t) * (rng.random() * 2 - 1)
        elif kind == "whoosh":
            frequency = 180.0 + 1800.0 * min(1.0, t / duration)
            value = 0.22 * math.sin(2 * math.pi * frequency * t) * (t / duration) * (1 - t / duration)
            value += 0.08 * (rng.random() * 2 - 1) * (t / duration) * (1 - t / duration)
        else:
            value = 0.3 * _fade(t, duration) * math.sin(2 * math.pi * 440.0 * t)
        rendered.append(value)
    write_pcm16(path, rendered, sample_rate, 1)
    return {"duration": duration, "sample_rate": sample_rate, "channels": 1, "seed": seed, "preset": kind}
