# 工作项目配置

Audio Forge 的本地工具和模型配置属于工作项目，不写入系统环境变量。

在工作项目根目录创建 `audioforge.config.json`：

```json
{
  "voice": {
    "backend": "piper",
    "executable": ".venv/Scripts/piper.exe",
    "model": "models/voices/zh_CN.onnx"
  }
}
```

`executable` 和 `model` 都相对于配置文件所在目录解析。它们可以指向工作目录的 `.venv`，但 Audio Forge 不会自动创建或填充 `.venv`。配置文件可以位于生成项目的任意父目录，CLI 会从当前目录和输出项目目录向上查找。

也可以显式指定配置：

```powershell
python -m audioforge generate voice `
  --text "任务完成" `
  --config .\audioforge.config.json `
  --output .\renders\voice-task-complete
```

`--piper` 和 `--model` 只用于单次覆盖，不是项目配置的替代方案。

