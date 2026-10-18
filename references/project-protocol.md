# AudioProject 协议

`project.json` 是 Audio Forge 与未来浏览器编辑器之间的最小交换格式。

## 路径规则

- 所有文件路径相对于项目根目录。
- JSON 中统一使用 `/`。
- 音频文件放在 `stems/` 或 `renders/`。
- 时间单位统一为秒。

## 核心字段

```json
{
  "version": "1",
  "title": "example",
  "kind": "music|sfx|voice",
  "backend": {"name": "procedural|piper"},
  "inputs": {},
  "tracks": [],
  "events": [],
  "automation": [],
  "loop": null,
  "analysis": {},
  "outputs": ["renders/example.wav"]
}
```

浏览器编辑器可以修改 `tracks`、`events`、`automation` 和 `loop`，再由本地 CLI 重新生成输出。v1 不要求浏览器直接执行 Piper 或 Python 合成器。
