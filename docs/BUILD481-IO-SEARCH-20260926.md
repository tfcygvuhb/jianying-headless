# macOS 26.6.2 安全目录遍历修复

2026-09-26，对已登记的 Build 481 2× 隔离草稿执行当前 live `verify` 曾连续 180 秒无输出，GUI 因预检未通过而未启动。前后 85 个目标文件的 SHA-256 清单一致。单独 `doctor` 约 5 秒通过。

隔离堆栈与 `sample` 将阻塞定位在 `bridge/runtime_io.py` 为 codec 哈希检查逐级打开 `~/Documents` 时的内核 `openat`。对 `Documents`、`Movies` 使用 `O_RDONLY` 打开目录均会超时；`stat` 与直接访问子文件正常。它不是草稿帧数、codec 字节哈希或 Python 发行版差异。原始采样、路径和 flags 矩阵位于 `work/build481-verify-hang-diagnostic-20260926/`。

macOS 上的目录遍历现改用 `O_SEARCH`，继续同时要求 `O_DIRECTORY`、`O_NOFOLLOW`、`O_CLOEXEC`，并在每一级打开后检查目录类型。其他平台保留原打开方式。隔离真实符号链接目录仍被拒绝。经已安装 Skill 正式入口复测，同一 2× 隔离工程 live `verify` 返回 `verified`，四镜像相同、源素材 SHA 不变；这只修复验证器的目录访问，不使 2× 导出开放。

回归包括 65 项仓库单测、39 项原生导出守卫、`doctor`、包与源码哈希检查。另对 1× 隔离工程执行正式原生导出，获得标准 `isom` H.264/AAC、90/90 帧并完整解码；此次视频和音频的全部解码帧 MD5 均与此前已逐帧 OCR 验收的 1× 成片一致。证据在 `work/build481-search-dir-postfix-export-1x-20260926/`。

此修改只涉及 Python IO 的**目录句柄**打开方式，不更改普通文件读取、codec 二进制、草稿或剪映程序。C++ codec 的加密写入父目录仍使用 `O_RDONLY`，尚需独立评估；本次不能由解密/导出成功推断新草稿构建与编辑写入在受保护目录下全部正常。
