# 剪映 11.4.0 Build 481 分阶段验收

本页只适用于精确运行档案 `jy14-headless-macos-11.4.0-build481`。它记录证据，
不因为某项离线测试通过而自动开启能力。应用签名、Team ID、动态库和 codec 哈希仍由
`doctor` 每次重新核对。

## 当前结论

| 分类 | 结果 |
| --- | --- |
| 已验证 | 精确应用身份；profile 专用 codec；基础视频、文字、音频的离线构建；`publish`（首页登记、热注册和冷重开）；`existing_edit`（文字替换/音量编辑副本登记）；`verify-build`/`verify` 回读；三类基础素材各三次隔离原生导出及正式 skill 入口复核；三类各自独立的 GUI 保存与冷重开；1.5×/0.75× 恒定变速的历史抽样时间码与三次导出，以及 0.1×/0.5×/8× 的历史单项导出、组合 GUI 冷重开和正式入口复核；后续逐帧复核发现非 1× 缺陷或证据不足，当前仅 1× 开放；Monaco TTF、固定 SHA 的 Arial TTF、STIXGeneralItalic OTF 与显式生成的 STIXGeneral Regular 别名、原 Skill 线性关键帧通道的隔离导出、GUI 冷重开及正式 Skill 导出；六种几何蒙版逐项 GUI 身份/缓存核验、保存冷重开与正式 Skill 导出；叠化及轻微抖动各自精确子集的 GUI、固定资源和正式 Skill 导出验收 |
| 部分验证 | STIXGeneral Regular 原始 OTF 隔离导出成功，但 GUI 保存把字体绑定改为应用系统字体，冷重开 `verify` 失败；其他静态字体没有逐项验收。2× 的隔离原生导出有 89/90 帧反例，其余未列倍率仅有离线构建或无证据。编辑副本冷重开 UI 有首轮记录；GUI 导出完成解码及视听检查，但它的 `major_brand=qt  `，不能作为标准 MP4 对照。LLDB 无法附加，但默认请求构造器经静态分析和独立 helper 动态验证 |
| 未验证 | 曲线变速；贴纸、调整图层；复合片段；叠化和轻微抖动以外的特效；其余高级功能的逐项冷重开与导出 |
| 明确阻断 | `native_resources` 总门禁关闭；Build 481 导出入口对未验收的自定义字体、其他转场、六种之外的蒙版、其他特效和曲线变速继续失败关闭；复合片段保存持久化存在失败记录 |

最近一次只读基线（2026-09-24）中，`doctor` 检查到 `publish=true`、
`existing_edit=true`、`native_export=false`、`native_resources=false`，完整身份、
运行库与 codec 哈希均匹配。命令、测试、工具链和源码哈希记录见
[Build 481 基线报告](BUILD481-BASELINE-20260924.md)。
这行是修改前的基线；当前基础导出已单独开启为 `native_export=true`。

## 阶段 1：publish

状态：`enabled`，`publish=true`（2026-09-23）。`com.apple.provenance` 和
`com.apple.macl` 是已记录的 macOS APFS/TCC 新 inode 扩展属性。安全元数据检查允许这两项
系统属性差异，其余内容、ACL、mode、owner/group 必须匹配。三次真实 staging 均满足此条件。

验证链路：
1. 首次 `publish`：build → verify-build → publish → 首页登记 → 打开 UI → 播放 → 保存 → 正常退出
2. 热注册验证：第二次 `resume-publish` 返回 `already_registered`
3. 冷重开验证：重启剪映后草稿 `Codex-Build481-Publish-20260923` 仍在首页，可 `verify` 通过
4. 索引 SHA 从原始 `5d206512...` 更新至 `e564f3c9...`，已有草稿和素材均未变化

早期隔离夹具和 staging 审计确实发现新 inode 会带来系统 provenance 属性，也曾因按字节
比较全部 xattr 而得到 `exact_runs=0/3`。该结果是旧检查口径下的历史失败记录；不能据此声称
当前门禁仍关闭。更新后的检查显式识别已审核的 macOS 属性，之后完成了三次真实 staging、
首页登记、UI 打开/播放/保存、正常退出、冷重开与结构回读。首页索引及原草稿未被意外改写。

## 阶段 2：existing_edit

状态：`enabled`，`existing_edit=true`（2026-09-23）。

在 publish 链路上叠加验证：
1. 对已 publish 草稿 `Codex-Build481-Publish-20260923`（3 轨：2 视频 + 1 文字 + 1 音频）
   执行只读 `inspect`，源文件 38 个前后 SHA 一致
2. 创建 edit plan：替换文字 + 修改音频音量
3. `build` 成功，`verify-build` 通过
4. `publish` 到首页（新草稿 `Codex-Build481-Edited-20260923`），返回 `created`
5. 源草稿字节不变，四份镜像精确相等，回读 ID 集合严格验证
6. 受限：仅支持单时间线、无云身份、无复合片段/转场/滤镜/蒙版；字体使用系统默认

已知限制：速度修改受计时一致性检查，需遵循 `extra_material_refs` 策略；编辑副本 UI
冷重开目前有首轮通过记录，尚未按多轮验收要求重复。副本流程限制为单时间线、无云身份、
无复合片段/转场/滤镜/蒙版，字体使用系统默认。

2026-09-26 在当前 macOS 26.6.2 上重验历史隔离副本：`edit verify-build` 通过，
但已保存的 live 副本 `edit verify` 先拒绝 `last_modified_platform.os_version`
由 26.5.1 到 26.6.2 的变化。只在内存中消除该差异继续诊断，又先后遇到三个
默认片段 `speed=1` 和根 `fps` 字段被原生保存省略。旧副本不能以此证明当前主机
完整 GUI 冷重开及正式导出；生产校验没有为通过此样本而放宽，仍需新的隔离副本
逐字段与逐帧验收。

## 阶段 3：native_export

状态：基础素材与 1× 正式导出 `enabled`，`native_export=true`；非 1× 倍率在正式登记和导出前拒绝，其他高级资源与运动能力保留独立门禁。

GUI 导出一次完成 `ffprobe`、完整解码、抽帧和音频检查，但实际 `major_brand=qt  `，
因此 GUI 文件的严格 MP4 容器验收未通过。LLDB 附加主进程、
服务子进程及受控启动均被 macOS 拒绝。静态分析随后定位默认请求构造器
`0x2681f98` 和 `0x3d8` 对象大小，并经隔离 helper 真实导出验证。完整过程见
[A+C 运行时取证](BUILD481-AC-RUNTIME-20260924.md)与
[请求结构分析](BUILD481-EXPORT-STATIC-20260924.md)。

混合时间线连续三次隔离原生导出成功；基础视频、文字、本地 WAV 各三次独立导出也成功。
每次均有进程退出码 0、恢复与编译完成事件、`ftypisom`、90 帧 H.264/AAC、
完整解码、源文件哈希不变；文字画面和 220/440 Hz 音频频谱核对通过。
正式 skill 入口再对三类构建各导出一次，均返回 `encoded-and-decoded`。
三类各自独立的新工程在剪映 GUI 打开、保存、完全退出并冷启动复开后均正常载入；
详见 [GUI 冷重开记录](BUILD481-GUI-REOPEN-20260924.md)。
恒定快慢速的独立样本三次导出和画面时间码采样均通过，组合草稿在剪映保存冷重开后
速度段仍存在；正式 Skill 对纯变速快照再导出一次，120/120 帧、标准 MP4 与完整解码均通过。
`native_export.py` 在创建输出目录前拒绝 Build 481 未验收的高级素材；已逐项验收的固定
叠化与轻微抖动资源通过各自精确门禁，不能据此开放总开关或其他资源。GUI 请求原始内存仍因系统调试限制没有取得，已用本机精确库指纹、
原生构造与实际输出闭环代替该项证据；出错回调的所有分支没有穷举。

## 阶段 4：native_resources

状态：`blocked`，`native_resources=false`；叠化与轻微抖动已通过独立精确子集门禁开放，不改变总门禁。

`doctor` 的 `resource_evidence` 给出字体、字幕、转场、滤镜、特效、贴纸、蒙版、
关键帧、复合片段、调整图层、会员/在线资源三层状态：`offline_build`、
`native_reopen`、`native_export`。该矩阵只描述证据，不能授予运行权限。

普通字幕、本地字体与线性关键帧的 Build 481 离线层为 `verified`；Monaco、固定 SHA 的 Arial TTF
与 STIXGeneralItalic OTF，以及显式生成的 STIXGeneral Regular 别名完成 GUI 保存冷重开、字体绑定回读和正式 Skill 导出，
原 Skill 支持的线性关键帧通道与六种几何蒙版完成各自的原生导出、GUI 保存冷重开和结构回读，
按固定字节/通道/资源 key 单项开放。叠化转场已由 Build 481 官方 GUI 完成资源选择、保存、
完全退出、冷重开及播放核验；GUI 成片为 QuickTime `qt  ` 容器，不能作为标准 MP4 证据。
同一精确资源又完成三次隔离 helper 导出和正式 Skill 导出：各 168/168 帧、`isom`、H.264/AAC、
完整解码通过。叠化样本音频仍需人工检查，保留同相双音约 +6.03 dB 警告。
轻微抖动已由 Build 481 官方 GUI 加入、保存和冷重开，确认 27 个源文件及两份 macOS 26.6.2
编译缓存身份。正式 Skill `build` → `verify-build` → `publish` → GUI 冷重开 → `verify` 全链路通过；
effect 轨 1 段、range 0.15、speed 0.33，缓存字节已验证、四镜像相等、源文件不变。正式导出通过，
90/90 帧、`isom`、H.264/AAC、完整解码。逐项证据见[叠化与特效验收](BUILD481-TRANSITION-EFFECT-20260924.md)。
已移除的滤镜不恢复；贴纸和调整图层没有实现证据；复合片段保存持久化已存在明确失败；
会员/在线资源不得以缓存存在或技术渲染代替账号和许可证明。原始 STIXGeneral Regular OTF 的 GUI 保存会将字体路径改为应用系统字体，`verify` 因 `Planned font binding changed` 失败；仅其精确 SHA 生成的本地别名已通过，其他字体未验。
原 Skill 从未声明曲线变速支持，因此不是本次 Build 481 会员资源适配项。详见[字体 GUI 验收](BUILD481-FONT-GUI-20260924.md)。
逐帧复核后恒速正式导出仅开放 1×，非 1× 异常及剩余倍率门禁见[恒速补验](BUILD481-SPEED-20260925.md)。

## 媒体格式补验（2026-09-24）

PNG、JPEG、GIF、HEVC 视频以及 MP3、WAV 音轨分别通过隔离 `build`、
`verify-build` 和原生导出；输出均为 90/90 帧标准 MP4，完整解码通过。
GIF 的三个时间点抽帧显示动画变化；MP3/WAV 用静音视频底片复验，输出中有
220 Hz 主峰而无底片原声的 440 Hz 主峰。输入与 build 哈希未变。
此外，GIF 独立草稿和包含这六种素材的 12 秒、三轨组合草稿均完成剪映保存、
正常退出、冷启动重开与正式 `verify`；组合工程保留四段视频、两条音轨，
PNG/JPEG/HEVC 的实际预览可见，GIF 两时刻画面发生变化，四镜像相同且源哈希未变。
2026-09-25 又经已安装 Skill 正式 `export` 对该组合 build 单独导出：
`work/build481-expanded-combined-media-export-20260925/result.json` 为
`encoded-and-decoded`，12 秒、360/360 帧、1280×720、30 fps、H.264/AAC、
`ftypisom`，`ffmpeg -xerror` 完整解码通过，源 build 未变；输出 SHA-256 为
`5f2d54d69f177383ecff6584a7e2685b75b99be53f5f769f4f3ae7318cf1d3e4`。
1.5/4.5 秒抽帧分别显示 PNG/JPEG，7.25/7.75 秒显示 GIF 红块位置变化，
10.5 秒显示 HEVC 测试色条。成片 1 秒和 4 秒音频各自有 220 Hz 主峰、RMS
约 0.088，7 秒无计划音轨时 RMS 为 0。组合成片仍没有主观听感结论；
上述单素材导出与频谱证据仍各自独立。
WAV 样本计划音量设为 0.5 时，输出实测增益约 0.352，不能把音量字段
直接当作线性振幅比例。数据保存在 `work/media-coverage-build481-20260924/`
的 `MEDIA-COVERAGE-20260924.md` 及 `gui-cold-reopen/gui-cold-reopen-acceptance.json`。

## 每次阶段完成的共同门槛

2026-09-26 当前 macOS 的安全目录遍历修复与正式 `verify`/1× 导出回归见
[O_SEARCH 诊断与验收](BUILD481-IO-SEARCH-20260926.md)。2× 内容映射门禁不变；
C++ codec 的 Build 481 专用目录访问修复、严格重建与新工程导出证据见
[Build 481 codec 目录写入报告](BUILD481-CODEC-SEARCH-20260926.md)。

- 独立 `work/` 夹具和验收报告；源草稿与所有输入媒体前后 SHA-256 一致。
- 全部单元测试、源码清单、`doctor`、`build`、`verify-build` 通过。
- 未解释的字段、资源、扩展属性、ACL、身份、回调或输出差异均失败关闭。
- 本地 `work/`、素材、草稿、日志、codec 和官方二进制不得加入 Git。
