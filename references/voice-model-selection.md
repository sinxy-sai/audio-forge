# 语音模型选择

Audio Forge 的语音后端按任务、资源成本和授权条件选择。模型权重属于工作项目，不提交到 `audio-forge` skill 仓库，也不由 skill 自动下载。

## 快速选择

| 需求 | 推荐 | 本地成本 | 当前状态 |
| --- | --- | --- | --- |
| 固定音色、低资源配音 | Piper | 低：通常几十到数百 MB | 已接入 |
| 中文或多语言声音克隆 | CosyVoice | 高：通常需要数 GB 模型目录和较强 GPU | 已接入本地 zero-shot 推理 |
| 中文定制音色和少样本训练 | GPT-SoVITS | 高：训练、显存和依赖成本高 | 计划评估 |
| 轻量音色转换 | OpenVoice | 中 | 计划评估 |
| 普通语音转文字 | faster-whisper small + int8 | 中低：约数百 MB到 1 GB | 已接入 |
| 高准确率语音转文字 | faster-whisper medium/large-v3 | 高：约 1.5–4 GB | 可选配置 |
| 低配置 CPU 转录 | whisper.cpp | 低到中 | 可选配置 |

## 配音和声音克隆

### Piper

适合固定音色、短句、游戏和产品原型。它启动快、资源占用低，当前是 Audio Forge 的默认配音后端。

Piper 通常使用 ONNX 声音模型。单个中文模型常见为几十到数百 MB，具体取决于语言、声学模型和量化方式。

### CosyVoice

适合参考音频驱动的中文或多语言声音克隆。CosyVoice 的模型目录通常包含多个组件，不能只按一个权重文件估算：

- 约 1–2 GB：较小或量化部署
- 约 2–4 GB：常见 0.5B 级完整模型目录
- 更高配置可能需要 GPU 和更多显存

实际大小随 CosyVoice 版本、精度、声码器和运行时变化。Audio Forge 使用隔离的 CosyVoice Python 环境和本地源码/模型目录运行 zero-shot 推理。参考音频应与同名 `.lab` 文本配对；CLI 的 `--text` 是新的合成文本。Audio Forge 不自动下载 CosyVoice 权重。

### GPT-SoVITS、OpenVoice、F5-TTS

这些模型可以作为后续后端，但选择依据不同：

- GPT-SoVITS：中文定制音色和训练能力强，部署复杂。
- OpenVoice：快速音色转换和原型验证，部署相对轻量。
- F5-TTS：自然度和风格实验较好，GPU 与授权要求需要单独确认。

使用他人声音前必须确认授权，同时检查代码、模型和训练数据的许可证。

## 语音识别

Whisper 是语音识别模型，负责把声音转换为文字。它不负责声音克隆。

### faster-whisper

`faster-whisper` 是 Whisper 的高性能本地实现，使用 CTranslate2 模型目录。常见磁盘占用范围如下：

| 模型 | 典型占用 | 适合 |
| --- | ---: | --- |
| tiny/base | 约 100–300 MB | 快速测试、低配置 |
| small | 约 500 MB–1 GB | 一般中文转录，推荐起点 |
| medium | 约 1.5–2.5 GB | 更高准确率 |
| large-v3 | 约 3–4 GB | 高质量批量转录 |

`int8` 可以降低内存和显存占用；`float16` 通常更适合 GPU。Audio Forge 当前支持配置本地 `faster-whisper`；tiny 适合快速试用，`small + int8` 是更好的中文起点。

### 其他识别运行时

- `whisper.cpp`：C++ 本地运行时，适合 CPU、桌面和便携部署。
- SenseVoice：中文和多语言场景，适合较低延迟任务。
- Paraformer / FunASR：中文实时识别和工程集成较强。
- sherpa-onnx：跨平台 ONNX 推理运行时，可作为统一本地运行层。

## ONNX 是什么

ONNX（Open Neural Network Exchange）是机器学习模型交换格式，不是音频格式。模型以计算图形式保存，可由 ONNX Runtime 在 CPU、CUDA、DirectML 或其他执行后端上运行。

在 Audio Forge 中：

```text
Piper          通常使用 .onnx 声音模型
faster-whisper 通常使用 CTranslate2 模型目录
CosyVoice     通常使用 PyTorch 或专用模型目录
```

## 工作项目配置原则

模型、可执行文件和参考音频放在工作项目中，例如：

```text
work-project/
├─ .venv/
├─ models/
│  ├─ voices/
│  │  └─ piper/
│  ├─ cosyvoice/
│  └─ asr/
├─ assets/
│  └─ reference-audio/
│     └─ <speaker>/
│        ├─ clip-001.wav
│        └─ clip-001.lab
└─ audioforge.config.json
```

`assets/reference-audio/` 保存参考 WAV 及其同名 `.lab` 文本；`models/` 保存本地模型目录；`projects/` 保存生成的 AudioProject。Audio Forge 只读取配置、检查文件、调用已安装后端并记录 metadata。它不自动创建 `.venv`，不自动下载权重，也不把模型文件复制进生成项目。

推荐配置形状：

```json
{
  "voice": {
    "backend": "piper",
    "executable": ".venv/Scripts/piper.exe",
    "model": "models/voices/zh_CN.onnx"
  },
  "voice_clone": {
    "backend": "cosyvoice",
    "model": "models/cosyvoice/CosyVoice2-0.5B",
    "reference_root": "assets/reference-audio",
    "reference_audio": "assets/reference-audio/<speaker>/clip-001.wav"
  },
  "asr": {
    "backend": "faster-whisper",
    "model": "models/asr/small",
    "compute_type": "int8"
  }
}
```

`voice_clone` 仍是预留配置；Piper 是已接入的语音生成后端，faster-whisper 是已接入的语音识别后端。
