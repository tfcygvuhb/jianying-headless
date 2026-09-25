# Build 481 A+C 运行时取证（2026-09-24）

本记录仅适用于本机签名的剪映专业版 11.4.0 Build 481（arm64）及
`libvideoeditor.dylib` SHA-256
`aea79715de6097394c2f38153e11565f02a823678801cd1eafe90bcccb20c086`。
调试对象是已登记的隔离工程 `Codex-Build481-Export-20260923`，
时间线包含本地测试视频、普通文字和本地音频。没有修改剪映程序或原始素材。

## A：请求对象抓取

- 对剪映主进程及 `--lvve-service` 子进程执行 LLDB `process attach`，两者均返回
  `Not allowed to attach to process`。对官方主程序执行 LLDB
  `process launch --stop-at-entry` 也被同一机制拒绝。
- 因无法在 GUI 的 `ExportClient::exportStart` 调用处中断，**未取得**GUI 中真实请求对象的
  原始内存快照。先前的轻量 `ReqStruct` 路由日志不是这类证据。
- 后续静态追踪找到了 Build 481 arm64 的 `ExportStartReqStruct` 默认构造函数
  `0x2681f98` 和 `0x3d8` 对象大小，另见
  [专用静态分析](BUILD481-EXPORT-STATIC-20260924.md)。旧 `0x2125188` 是从源对象复制的路径，
  不是默认构造器；先前 `0x150` 假设已由交叉证据推翻。
- arm64 符号地址 `0x00103548`；已定位的库内调用点 `0x002681758` 是同一映像内的
  直接 `BL`，不是 dyld 导入桩。因此即使应用允许 DYLD 环境变量，普通
  `DYLD_INTERPOSE` 也不能截获这条内部调用。匿名 `0x002125188` 路径读取源
  `shared_ptr` 并分配 `0x150` 字节，尚不能作为已验证的默认工厂。

## C：GUI 导出对照

在剪映 GUI 中打开上述隔离工程，将格式设为 MP4，并只导出到忽略版本控制的
`work/build481-ac-20260924/gui-export/`。界面显示“导出成功”。所得文件 SHA-256 为
`0df1833c2376131789d6cee1fce2626fd1d2d3bb69b720659fbe21111420a868`。
`ffprobe` 检查为 3.000 秒、1920×1080、30 fps、90 帧 H.264 视频和 AAC 音轨；
尽管界面选择 MP4、文件扩展名为 `.mp4`，容器的 `major_brand` 实际为 `qt  `。
因此该 GUI 对照不能视为本项目严格 MP4 容器验收通过。
`ffmpeg -xerror` 完整解码成功。中间帧显示预期的蓝底及
“Native Export Test”文字；音频流非空，峰值约 -23.5 dB。

这只证明 GUI 能处理该隔离工程。GUI 的 QuickTime brand 与下述 helper 输出不同，
不能把 GUI 文件作为标准 MP4 对照文件。

## C：隔离 helper 原生导出验收

采用精确 Build 481 库指纹和该版本默认构造器，恢复后从独立 helper 调用原生
`ExportService`。先前的混合视频、文字、音频时间线连续三次成功；随后分别对纯视频、
普通文字、本地 WAV 各运行三次新的独立导出作专项检查。每次都记录退出码 0、
`JY_NATIVE_RESTORE_DONE`、`VE_INFO_COMPILE_DONE`、`JY_NATIVE_EXPORT_DONE`、
实际 `ftypisom`、90 帧 H.264/30 fps/1920×1080、AAC 音轨、约 3 秒时长、
`ffmpeg -xerror` 完整解码、输入资源与原 build 哈希一致。九次记录保存在忽略目录
`work/build481-ac-20260924/category-exports/{video,text,audio}-{1,2,3}/result.json`。

画面抽样显示纯视频的测试色条；文字版中间帧清晰出现 `Build 481 Text`。
音频 FFT 显示源视频的 440 Hz 正弦保留，本地 WAV 的 220 Hz 正弦在音频版出现；
三次音频版都有相同的 220 Hz 峰，符合计划中的 0.5 音量混音。
随后使用 repo/已安装 skill 的正式 `export` 入口对隔离 build 复核：
正式视频、文字和本地音频输出返回 `encoded-and-decoded`，源 build 未改变；
其产物和审计记录位于 `work/build481-ac-20260924/official-{video,text,audio}-1/`。

这些验证支持开启 Build 481 的**基础原生导出**。`native_resources` 仍关闭；
导出入口在创建作业前拒绝该版本未验收的转场、蒙版、特效、自定义字体、曲线变速和关键帧。
GUI 冷重开与高级功能逐项验收另行记录。LLDB 在本机无法附加的限制仍然存在。

另为恒定变速制作仅含本地带时间码视频的隔离快慢速样本：1.5× 段目标 2 秒对应
源 3 秒，0.75× 段目标 2 秒对应源 1.5 秒。三次独立 helper 导出均为 4 秒、120 帧，
还原/编译/导出事件齐全、标准 MP4、完整解码且源字节不变。输出在 0.5/1.5 秒的
加速段显示源约 0.733/2.233 秒；在 2.5/3.5 秒的减速段显示源约
0.400/1.133 秒，符合最近帧采样。组合变速草稿也经剪映保存并冷重开，界面显示
两段各 2 秒并可播放至 4 秒。已安装 Skill 正式 `export` 入口再次导出纯变速样本，
输出 120/120 帧、H.264/AAC、`ftypisom`、完整解码且 source build 未变。
证据见 `work/build481-ac-20260924/official-speed-timecode-1/` 与
`work/build481-ac-20260924/native-trial1/speed-timecode-*`。

## 错误路径对照

在独立 `work/build481-ac-20260924/native-error-probe-path2/` 中，临时 helper
仅将运行时快照存放于作业根目录，并把 MP4 目标指定到当前进程不可写的作业子目录。
原生服务完成恢复后报告 `exportcallback compile_error_callback ... prepareWriterFailed... -115`；
更新后的 helper 将该真实错误回调识别为失败，退出码为 1，未发出
`JY_NATIVE_EXPORT_DONE`，也没有可交付的 MP4。该改动只进入隔离试验源码，
正式版本仅新增该错误事件的 fail-closed 识别。
随后用更新后的正式 helper 再导出一次基础视频，仍返回
`encoded-and-decoded`、90/90 帧、`ftypisom`、完整解码与源 build 未变；
审计位于 `work/build481-ac-20260924/official-video-2/`。

另一次只在隔离副本中把原生 MP4 writer selector 改为 255，虽完成编码，实际
`major_brand=qt  `。正式出口的原始 `ftyp` 检查会拒绝这种结果，说明完成事件和
`ffprobe` 流信息本身不足以判定标准 MP4 合格。两项试验均未修改剪映程序、
用户原草稿或正式 helper 的编码选择。
