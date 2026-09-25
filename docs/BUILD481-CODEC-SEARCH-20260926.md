# Build 481 专用 codec 的受保护目录写入

2026-09-26，当前 macOS 26.6.2 上，原 Build 481 codec 在 `~/Documents` 下创建新的加密元数据文件时超过 8 秒仍阻塞在目录打开，未创建输出。根因与 Python 验证器的目录遍历相同：对受保护目录使用 `O_RDONLY | O_DIRECTORY`。原版 codec SHA-256 为 `f6f49c718c740dae77fe1525b2762fc1801951ec6bf5eb223156842529123947`，原二进制备份保存在忽略提交的 `work/build481-cpp-codec-search-prototype-20260926/`。

新增 `bridge/jy14_codec_build481.cpp`，仅将输出父目录逐级打开的两处 `O_RDONLY` 改为 `O_SEARCH`，保留 `O_DIRECTORY`、`O_NOFOLLOW`、`O_CLOEXEC`、逐级检查、`O_EXCL` 禁止覆盖和输出权限。原 `bridge/jy14_codec.cpp` 字节不变；11.4.0 历史 profile、11.4.2 和 11.5.0 继续选择原源码及原哈希。仅精确 `11.4.0 Build 481` 选择新源码和 SHA-256 `a473977dabb7652b7f111cd5d279c697ae71afc94c64a137d85fc8af8d06203f`。在匹配的 Apple clang 21.0.0、SDK 26.5 下，最终文件名编译两次得到相同哈希，正式 `build_native_codec.py --rebuild-check` 再次复现该哈希。原源码编译为原 Build 481 文件名仍复现旧哈希。

隔离原型对 `~/Documents` 下的新输出在 1.314 秒完成加密，逐字节解密 73 字节原文成功；重复写入同名文件被拒绝且原哈希不变，符号链接父目录被拒绝且目标未产生文件，创建的文件权限是 `0600`。原始编译与测试 JSON 保留在 `work/build481-cpp-codec-search-prototype-20260926/`。

正式已安装 Skill 入口使用新 codec 在新的隔离工程完成 `build`、`verify-build`、`publish` 和 live `verify`；草稿含两段视频、一段普通文字与一段本地音频，四镜像一致、源文件 SHA-256 不变。随后的原生导出得到 1920×1080、30 fps、H.264/AAC、`isom`、150/150 帧、4.999998 秒，完整解码成功。抽帧图中先出现蓝色视频、中央白字，后切换红色视频；音频频谱及静音检测显示前 3 秒有声音、后约 2 秒静音，符合计划中 3 秒音频素材。详细审计、画面和音频图位于 `work/build481-cpp-codec-formal-20260926/`。

回归：仓库单测 65/65，原生导出守卫 39/39，包/源码哈希检查、`doctor` 和已安装 Skill 同步检查通过。旧版本二进制在本机仓库中不存在，因而旧版本本机运行测试未做；旧版本源码、选择分支和原 pin 保持不变。这个新工程尚未通过剪映 GUI 保存和冷重开：当时 macOS 会话检查仍报告屏幕锁定，故没有启动剪映。该实验只证明受保护目录下的构建/登记/校验/原生导出链路；GUI 验收与其他高级能力继续按各自门禁失败关闭。
