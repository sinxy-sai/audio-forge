"""Local faster-whisper transcription backend."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import AsrConfig


class TranscriptionUnavailable(RuntimeError):
    """Raised when faster-whisper cannot transcribe an audio file."""


def transcribe_audio(
    audio: Path,
    *,
    asr: AsrConfig,
    language: str | None = None,
    beam_size: int = 1,
    vad_filter: bool = True,
) -> dict[str, Any]:
    if not audio.is_file():
        raise TranscriptionUnavailable(f"audio file does not exist: {audio}")
    if beam_size < 1:
        raise ValueError("beam_size must be at least 1")
    try:
        from faster_whisper import WhisperModel
    except ImportError as error:
        raise TranscriptionUnavailable(
            "faster-whisper is not installed in the active Python environment"
        ) from error

    try:
        model = WhisperModel(str(asr.model), device=asr.device, compute_type=asr.compute_type)
        segments, info = model.transcribe(
            str(audio),
            language=language,
            beam_size=beam_size,
            vad_filter=vad_filter,
        )
        rows = [
            {"start": segment.start, "end": segment.end, "text": segment.text.strip()}
            for segment in segments
        ]
    except Exception as error:  # backend errors vary by runtime and device
        raise TranscriptionUnavailable(f"faster-whisper failed: {error}") from error

    return {
        "backend": "faster-whisper",
        "model": asr.model.as_posix(),
        "device": asr.device,
        "compute_type": asr.compute_type,
        "language": info.language,
        "language_probability": info.language_probability,
        "segments": rows,
    }


def write_transcription(root: Path, audio: Path, result: dict[str, Any]) -> tuple[Path, Path]:
    analysis = root / "analysis"
    analysis.mkdir(parents=True, exist_ok=True)
    try:
        audio_ref = audio.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        audio_ref = audio.resolve().as_posix()
    payload = {"audio": audio_ref, **result}
    json_path = analysis / "transcript.json"
    text_path = analysis / "transcript.txt"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [f"[{segment['start']:.2f}–{segment['end']:.2f}] {segment['text']}" for segment in result["segments"]]
    text_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return json_path, text_path
