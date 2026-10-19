"""One-shot worker kept in the isolated CosyVoice Python environment."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


def main(request_file: str) -> int:
    request = json.loads(Path(request_file).read_text(encoding="utf-8"))
    source = Path(request["source"]).resolve()
    model_dir = Path(request["model"]).resolve()
    tokenizer = model_dir / "speech_tokenizer_v2.onnx"
    batch_tokenizer = model_dir / "speech_tokenizer_v2.batch.onnx"
    if not tokenizer.is_file() and batch_tokenizer.is_file():
        shutil.copyfile(batch_tokenizer, tokenizer)
    required = (model_dir / "cosyvoice2.yaml", model_dir / "llm.pt", model_dir / "flow.pt", model_dir / "hift.pt")
    if not any((model_dir / name).is_file() for name in ("cosyvoice.yaml", "cosyvoice2.yaml", "cosyvoice3.yaml")):
        raise FileNotFoundError(f"CosyVoice model config not found under: {model_dir}")
    missing = [path for path in required[1:] if not path.is_file()]
    if missing:
        raise FileNotFoundError("incomplete local CosyVoice model; missing: " + ", ".join(map(str, missing)))
    sys.path.insert(0, str(source / "third_party" / "Matcha-TTS"))
    sys.path.insert(0, str(source))
    import torch
    import torchaudio
    from cosyvoice.cli.cosyvoice import AutoModel

    model = AutoModel(model_dir=str(model_dir))
    pieces = [item["tts_speech"].detach().cpu() for item in model.inference_zero_shot(
        request["target_text"], request["reference_text"], request["reference_audio"], stream=False
    )]
    if not pieces:
        raise RuntimeError("CosyVoice returned an empty speech result")
    speech = torch.cat(pieces, dim=1)
    output = Path(request["output"])
    output.parent.mkdir(parents=True, exist_ok=True)
    torchaudio.save(str(output), speech, model.sample_rate, encoding="PCM_S", bits_per_sample=16)
    print(json.dumps({"sample_rate": model.sample_rate, "frames": speech.shape[-1]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
