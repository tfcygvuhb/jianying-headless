# yichen-jianying-edit

这是 Jianying Headless 的独立 Agent Skill，包含说明、口播计划编译器及固定哈希的
调用入口。它不包含剪映引擎，也不把核心源码复制进安装后的 Skill 目录。

Skill 公开收录于 [yichen-skills](https://github.com/mcncarl/yichen-skills/tree/main/yichen-jianying-edit)，
核心项目也已公开；仍需单独检出核心代码并安装匹配版本的剪映。

## 安装

1. 检出 [mcncarl/jianying-headless](https://github.com/mcncarl/jianying-headless) 的公开源码。
2. 在核心仓库运行 `python3 tools/build_native_codec.py`，然后执行本 Skill 的 `doctor`。
3. 将本目录作为一个完整 Skill 安装到宿主支持的技能目录；不要只复制 `SKILL.md`。
4. Skill 不在核心仓库内时，设置 `JIANYING_HEADLESS_ROOT=/absolute/path/to/jianying-headless`。

```bash
python3 /absolute/path/to/yichen-jianying-edit/scripts/headless_draft.py doctor
```

路径和环境变量只在用户本机配置，不写入 Git。Skill 会校验核心组件的固定哈希；
源码变更后需要重新验证和同步入口，不能静默接受任意其他版本。

## 运行前提

Apple Silicon macOS、Python 3.9+、FFmpeg / ffprobe、Xcode 编译工具，以及匹配版本的
原版剪映。11.5.0 为主版本，11.4.2 为兼容版本，两者支持草稿和原生导出；
普通 11.4.0 仅保留历史草稿配置。精确的 11.4.0 Build 481 档案已通过离线新建草稿、
首页登记、结构检查、已有工程独立副本编辑，以及本地视频、文字、本地音频的基础原生 MP4
导出；0.1×、0.5×、0.75×、1×、1.5×、8× 六档恒速、Monaco TTF、固定 SHA
`525979822591a3447cfc49d943d6f7683508e25543407871c0ed8fed05fd2bd9` 的 Arial TTF 与固定 SHA `7f6bf9cab728febe4ce111bbfbcd16253806dcab0bbe1940ede2782cfc319a72` 的 STIXGeneralItalic OTF、线性关键帧、六种几何蒙版、固定叠化 `transition/dissolve` 和轻微抖动 `effect/light-shake` 也已通过单项验收。叠化和轻微抖动正式原生导出分别为 168 和 90 帧 H.264/AAC，完整解码通过。仅匹配固定资源 key、文件清单及 SHA 时开放；`native_resources` 总门禁仍关闭。Build 481 的原始 STIXGeneral Regular OTF GUI 保存失败；显式生成的固定 SHA 别名已通过验收，其他字体仍关闭。
原 Skill 不支持曲线变速；其他未逐项验收的字体/原生资源仍未开放。
导出快照必须与当前运行版本一致。
精确工具链和哈希限制见核心项目说明；这不是任意 Mac/任意剪映版本的兼容承诺。

剪辑计划可以直接由用户或 Agent 提供，不强制使用付费 ASR。`asr_once.py` 仅是可选
去重包装器，需要另行提供兼容的转写执行器；`YICHEN_ASR_EXECUTOR` 可以指定它的
本机路径，默认检查当前用户的 `scripts/transcribe.py`。该执行器及任何凭据不随包分发。

详细操作见 [SKILL.md](SKILL.md)。本 Skill 不授权自动上传视频、公开草稿、购买资源
或将剪映官方文件重新分发。来源和许可边界见
[dependencies-and-notices.md](references/dependencies-and-notices.md)。

## 许可

原创部分采用[个人学习和非商业使用条款](LICENSE)，商业用途须取得作者明确书面授权。
第三方内容保留各自原许可证；本 Skill 不授予剪映程序库、账号、素材或服务的使用权。
