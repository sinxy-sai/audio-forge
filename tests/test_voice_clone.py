import json
import tempfile
import unittest
import wave
from pathlib import Path

from audioforge.config import ConfigUnavailable, load_voice_clone_config
from audioforge.cli import build_parser
from audioforge.commands import generate
from audioforge.voice_clone import (
    CosyVoiceUnavailable,
    find_reference_candidates,
    read_reference_text,
    render_cosyvoice,
)


def write_wav(path: Path, *, sample_rate: int = 16000, frames: int = 80000, clipped: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    value = 32767 if clipped else 1000
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes((value.to_bytes(2, "little", signed=True)) * frames)


class VoiceCloneTests(unittest.TestCase):
    def test_same_stem_lab_is_used_and_bad_wavs_are_filtered(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            good = root / "good.wav"
            write_wav(good, frames=80000)
            (root / "good.lab").write_text("参考句子\n", encoding="utf-8")
            short = root / "short.wav"
            write_wav(short, frames=1000)
            (root / "short.lab").write_text("太短\n", encoding="utf-8")
            clipped = root / "clipped.wav"
            write_wav(clipped, clipped=True)
            (root / "clipped.lab").write_text("削波\n", encoding="utf-8")

            candidates = find_reference_candidates(root)

            self.assertEqual([candidate.audio.name for candidate in candidates], ["good.wav"])
            self.assertEqual(read_reference_text(good), "参考句子")

    def test_voice_clone_config_resolves_paths_and_reports_missing_model_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            python = root / "python.exe"
            source = root / "cosyvoice-src"
            model = root / "model"
            reference = root / "ref.wav"
            python.write_bytes(b"x")
            write_wav(reference)
            reference.with_suffix(".lab").write_text("参考句子\n", encoding="utf-8")
            source.mkdir()
            model.mkdir()
            config = root / "audioforge.config.json"
            config.write_text(json.dumps({
                "voice_clone": {
                    "backend": "cosyvoice",
                    "python": "python.exe",
                    "source": "cosyvoice-src",
                    "model": "model",
                    "reference_audio": "ref.wav",
                }
            }), encoding="utf-8")

            clone = load_voice_clone_config(str(config))
            self.assertEqual(clone.model, model.resolve())
            candidate = find_reference_candidates(root)
            with self.assertRaises(CosyVoiceUnavailable) as context:
                render_cosyvoice(
                    "目标句", root / "out.wav", config=clone,
                    candidate=candidate[0], reference_text="参考句子",
                )
            self.assertIn(str(model.resolve()), str(context.exception))

    def test_voice_clone_cli_keeps_lab_prompt_separate_from_target_tts_text(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_wav(root / "reference.wav")
            (root / "reference.lab").write_text("参考音频实际说的话", encoding="utf-8")
            (root / "python.exe").write_bytes(b"x")
            (root / "source").mkdir()
            (root / "model").mkdir()
            config = root / "audioforge.config.json"
            config.write_text(json.dumps({
                "voice_clone": {
                    "backend": "cosyvoice",
                    "python": "python.exe",
                    "source": "source",
                    "model": "model",
                    "reference_root": ".",
                }
            }), encoding="utf-8")
            args = build_parser().parse_args([
                "generate", "voice-clone", "--text", "目标 TTS 文本",
                "--config", str(config), "--output", str(root / "project"),
            ])

            self.assertEqual(args.kind, "voice-clone")
            self.assertEqual(args.text, "目标 TTS 文本")
            self.assertEqual(generate(args), 2)
            manifest = json.loads((root / "project" / "project.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["inputs"]["text"], "目标 TTS 文本")
            self.assertEqual(manifest["inputs"]["reference_text"], "参考音频实际说的话")
            self.assertEqual(manifest["outputs"], [])


if __name__ == "__main__":
    unittest.main()
