"""Reference-audio discovery and local CosyVoice orchestration."""

from __future__ import annotations

import audioop
import array
import json
import os
import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import VoiceCloneConfig


@dataclass(frozen=True)
class ReferenceCandidate:
    audio: Path
    transcript: Path
    duration: float
    sample_rate: int
    channels: int
    peak: float
    clipped_samples: int

    @property
    def score(self) -> tuple[float, float, str]:
        return (abs(self.duration - 6.0), -self.duration, self.audio.as_posix())


def read_reference_text(audio: Path) -> str:
    transcript = audio.with_suffix(".lab")
    if not transcript.is_file():
        raise FileNotFoundError(f"reference transcript does not exist: {transcript}")
    text = transcript.read_text(encoding="utf-8-sig").strip()
    if not text:
        raise ValueError(f"reference transcript is empty: {transcript}")
    return " ".join(line.strip() for line in text.splitlines() if line.strip())


def inspect_reference(audio: Path) -> ReferenceCandidate | None:
    transcript = audio.with_suffix(".lab")
    if not audio.is_file() or not transcript.is_file():
        return None
    try:
        with wave.open(str(audio), "rb") as handle:
            channels = handle.getnchannels()
            sample_rate = handle.getframerate()
            width = handle.getsampwidth()
            frames = handle.getnframes()
            raw = handle.readframes(frames)
        if width != 2 or channels not in (1, 2) or sample_rate <= 0:
            return None
        count = frames * channels
        if len(raw) != count * 2:
            return None
        peak = audioop.max(raw, 2) / 32767.0 if raw else 0.0
        samples = array.array("h")
        samples.frombytes(raw)
        clipped = sum(abs(value) >= 32767 for value in samples)
        duration = frames / sample_rate
        if duration < 1.5 or duration > 20.0 or peak < 0.01 or clipped:
            return None
        read_reference_text(audio)
    except (OSError, wave.Error, ValueError, UnicodeError):
        return None
    return ReferenceCandidate(audio, transcript, duration, sample_rate, channels, peak, clipped)


def find_reference_candidates(root: Path) -> list[ReferenceCandidate]:
    candidates = [candidate for audio in root.expanduser().resolve().rglob("*.wav") if (candidate := inspect_reference(audio))]
    return sorted(candidates, key=lambda item: item.score)


def choose_reference(config: VoiceCloneConfig) -> ReferenceCandidate:
    if config.reference_audio:
        candidate = inspect_reference(config.reference_audio)
        if candidate is None:
            raise ValueError(f"configured reference audio is not a valid clone candidate: {config.reference_audio}")
        return candidate
    candidates = find_reference_candidates(config.reference_root)
    if not candidates:
        raise ValueError(f"no usable WAV/.lab reference pair found under: {config.reference_root}")
    return candidates[0]


def candidate_report(candidate: ReferenceCandidate) -> dict[str, Any]:
    return {
        "audio": candidate.audio.as_posix(),
        "transcript": candidate.transcript.as_posix(),
        "duration": round(candidate.duration, 3),
        "sample_rate": candidate.sample_rate,
        "channels": candidate.channels,
        "peak": round(candidate.peak, 6),
        "clipped_samples": candidate.clipped_samples,
    }


class CosyVoiceUnavailable(RuntimeError):
    """Raised when the local CosyVoice runtime cannot render a request."""


def render_cosyvoice(
    text: str,
    output: Path,
    *,
    config: VoiceCloneConfig,
    candidate: ReferenceCandidate,
    reference_text: str,
) -> dict[str, Any]:
    if not text.strip():
        raise ValueError("target TTS text must not be empty")
    if not reference_text.strip():
        raise ValueError("reference text must not be empty")
    if not config.model.is_dir():
        raise CosyVoiceUnavailable(f"CosyVoice model directory does not exist: {config.model}")
    if not any((config.model / name).is_file() for name in ("cosyvoice.yaml", "cosyvoice2.yaml", "cosyvoice3.yaml")):
        raise CosyVoiceUnavailable(f"CosyVoice model config not found under: {config.model}")
    output.parent.mkdir(parents=True, exist_ok=True)
    request_path = output.parent.parent / "metadata" / "cosyvoice-request.json"
    request_path.parent.mkdir(parents=True, exist_ok=True)
    request_path.write_text(json.dumps({
        "source": str(config.source),
        "model": str(config.model),
        "reference_audio": str(candidate.audio),
        "reference_text": reference_text,
        "target_text": text,
        "output": str(output),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    environment = os.environ.copy()
    python_paths = [str(config.source), str(config.source / "third_party" / "Matcha-TTS")]
    existing = environment.get("PYTHONPATH")
    if existing:
        python_paths.append(existing)
    environment["PYTHONPATH"] = os.pathsep.join(python_paths)
    matplotlib_config = request_path.parent / "matplotlib"
    matplotlib_config.mkdir(parents=True, exist_ok=True)
    environment["MPLCONFIGDIR"] = str(matplotlib_config)
    worker = Path(__file__).with_name("cosyvoice_worker.py")
    completed = subprocess.run(
        [str(config.python), str(worker), str(request_path)],
        capture_output=True,
        text=True,
        env=environment,
        cwd=config.source,
        timeout=1800,
    )
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip() or "unknown CosyVoice error"
        raise CosyVoiceUnavailable(f"CosyVoice failed (exit {completed.returncode}): {detail[-5000:]}")
    if not output.is_file() or output.stat().st_size <= 44:
        raise CosyVoiceUnavailable("CosyVoice returned successfully but produced no usable WAV")
    with wave.open(str(output), "rb") as handle:
        output_sample_rate = handle.getframerate()
        output_channels = handle.getnchannels()
        output_width = handle.getsampwidth()
    if output_sample_rate <= 0 or output_channels not in (1, 2) or output_width != 2:
        raise CosyVoiceUnavailable("CosyVoice output is not a supported 16-bit PCM WAV")
    return {
        "backend": "cosyvoice",
        "python": config.python.as_posix(),
        "source": config.source.as_posix(),
        "model": config.model.as_posix(),
        "device": config.device,
        "sample_rate": output_sample_rate,
        "channels": output_channels,
        "sample_width": output_width,
        "reference_audio": candidate.audio.as_posix(),
        "reference_transcript": candidate.transcript.as_posix(),
        "reference_text": reference_text,
        "request": request_path.relative_to(output.parent.parent).as_posix(),
    }

