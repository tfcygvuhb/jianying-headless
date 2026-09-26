# Build 481 只读基线（2026-09-24）

本报告记录文档修正及适配工作开始前的状态。检查仅读取环境、源文件和测试夹具；测试输出
保存在忽略目录 `work/baseline-20260924/`，没有将素材、草稿或日志加入源码。

## 运行身份

| 项目 | 检查结果 |
| --- | --- |
| 主机 | Apple Silicon，`arm64`，MacBook Air |
| macOS | 26.6.2，Build 25G83 |
| 剪映 | 11.4.0，Build 481，Bundle ID `com.lemon.lvpro` |
| Team ID | `X2JNK7LY8J` |
| libvideoeditor SHA-256 | `aea79715de6097394c2f38153e11565f02a823678801cd1eafe90bcccb20c086` |
| runtime profile | `jy14-headless-macos-11.4.0-build481` |
| codec SHA-256 | `f6f49c718c740dae77fe1525b2762fc1801951ec6bf5eb223156842529123947` |
| 能力 | `draft_create=true`、`publish=true`、`verify=true`、`existing_edit=true`；`native_export=false`、`native_resources=false` |
| 身份检查 | 完整签名通过，运行库和 codec 哈希匹配；doctor 报告 `network_called=false` |

## 基线命令

- `python3 skills/yichen-jianying-edit/scripts/headless_draft.py doctor`：退出码 0，状态 `ok`。
- `python3 tools/check_package.py`：退出码 0，`source-checks-passed`，清点 83 个文件；源码清单 SHA-256 为 `f85c23143ee2c8557349a89ef082e22090c4220f755e85fda9f79a56b5c6b224`。
- `python3 -m unittest discover -s tests -v`：57 项通过。
- `git status --short`：开始时工作树干净。

## 工具链

Apple clang 21.0.0（`clang-2100.3.34.2`）、Xcode 27.0（Build 27A266a）、Python 3.9.6、
FFmpeg/ffprobe 9.0.2。doctor 和测试完整输出保存在本机 `work/baseline-20260924/`。

## 修改前源码哈希

以下哈希用于确认开始编辑时导出实现与相关组件的基线身份；它们不是新的 capability 授权：

| 文件 | SHA-256 |
| --- | --- |
| `engine/native_export.cpp` | `49dfe5f91e7177dfaf7dd76b28bb3b234dde2791fb2df2d2b6559218d47673d2` |
| `engine/native_export.py` | `380338e5946465c89cd89a31473fca5365807153245594e75d931fdfad2e90c8` |
| `engine/runtime_profiles.py` | `02404af45a3c9d17dff0804d8d6ec27e282d12248cc3b01fe248a40b330198c7` |
| `engine/headless_runtime.py` | `9925bd53c2cfc40844516aa3242a2cfb455843088d35bff53df5a9b123108443` |
| Skill `headless_draft.py` | `c1fbf6fa0631a1ca05981eeea0bc38e72cfebd40f48207c2c9cdbf0d55748ac7` |
