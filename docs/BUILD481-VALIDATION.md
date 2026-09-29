# 剪映 11.4.0 Build 481 分阶段验收

本页只适用于精确运行档案 `jy14-headless-macos-11.4.0-build481`。它记录证据，
不因为某项离线测试通过而自动开启能力。应用签名、Team ID、动态库和 codec 哈希仍由
`doctor` 每次重新核对。

## 当前结论

| 分类 | 结果 |
| --- | --- |
| 已验证 | 精确应用身份；profile 专用 codec；基础视频、文字、音频的离线构建；`publish`（新建工程首页登记、热注册和冷重开）；编辑副本离线构建与 `verify-build`；新建工程 `verify-build`/`verify` 回读；三类基础素材各三次隔离原生导出及正式 skill 入口复核；三类各自独立的 GUI 保存与冷重开；1.5×/0.75× 恒定变速的历史抽样时间码与三次导出，以及 0.1×/0.5×/8× 的历史单项导出、组合 GUI 冷重开和正式入口复核；后续逐帧复核发现非 1× 缺陷或证据不足，当前仅 1× 开放；Monaco TTF、固定 SHA 的 Arial TTF、STIXGeneralItalic OTF 与显式生成的 STIXGeneral Regular 别名、原 Skill 线性关键帧通道的隔离导出、GUI 冷重开及正式 Skill 导出；六种几何蒙版逐项 GUI 身份/缓存核验、保存冷重开与正式 Skill 导出；叠化及轻微抖动各自精确子集的 GUI、固定资源和正式 Skill 导出验收 |
| 部分验证 | 原始 STIXGeneral Regular OTF 在旧 GUI 样本保存后回退为系统字体，但另一份同 SHA 的隔离工程三轮保存冷重开保留草稿字段；缺字体面板身份与视觉 A/B 正对照，门禁不变。其他静态字体没有逐项验收。2× 的隔离原生导出有 89/90 帧反例，其余未列倍率仅有离线构建或无证据。编辑副本冷重开 UI 有首轮记录；GUI 导出完成解码及视听检查，但它的 `major_brand=qt  `，不能作为标准 MP4 对照。自定义曲线已有两份独立 GUI 工程完成保存、正常退出、冷启动重开和官方导出；第二份通过 185/185 全帧源标签、完整解码和 SSIM，但 GUI 容器为 `qt  `，且尚未接入正式 Skill 入口；同一第一份冷快照的三次 helper 输出不能替代通用计划证据。LLDB 无法附加，但默认请求构造器经静态分析和独立 helper 动态验证 |
| 实验性暂定通过 | 2× 恒速按使用者选择列为后续研发候选；这只表示优先级与阶段性状态。89/90 帧反例及 90/90 帧源画面映射偏差仍在，是否属于剪映 Build 481 本身尚未证明，正式登记和导出门禁保持关闭。当前优先攻坚曲线变速。 |
| 未验证 | 曲线变速的计划格式、通用构建和正式 Skill 出口；贴纸；调整图层的正式计划构建、helper/Skill 出口和多份独立样本；复合片段的结构一致性与正式 Skill 出口；叠化和轻微抖动以外的特效；其余高级功能的逐项冷重开与导出。自定义曲线、复合片段及调整图层各有隔离 GUI 冷重开和官方 GUI 导出样本，均不证明正式出口可用 |
| 明确阻断 | `native_resources` 总门禁关闭；Build 481 导出入口对未验收的自定义字体、其他转场、六种之外的蒙版、其他特效和曲线变速继续失败关闭；复合片段子编辑后 parent、sidecar 与组合 ID 不一致，生产门禁继续关闭 |

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

当前状态：仅离线操作 `existing_edit=true`，登记/正式导出 `existing_edit_publish=false`。以下是 2026-09-23 的历史实验记录，不代表当前入口开放。

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

2026-09-26 新的隔离 edit-build 现在把构建前后校验一致的 Build 481 runtime
身份直接写入 `build.json.runtime`，`verify-build` 与 live verify 对有此字段的
build 比对当前应用、库与 codec 指纹。独立新样本离线 build/verify-build 通过；
将记录中的 codec SHA 刻意改为全零，verify-build 在读取草稿前失败。历史
没有 runtime 字段的 v1 build 仍可作离线回读，但不能凭当前机器的身份给旧
样本补签，也没有进入 `gui-cycle` 的资格。此改动不改变
`existing_edit_publish=false`；当前编辑副本仍未完成 GUI 保存冷重开和正式
导出。隔离证据在 `work/build481-edit-runtime-embedded-20260926/`。

`gui-cycle` 现在按新建/编辑 build schema 分流：编辑副本须匹配完整构建时
runtime、源工程与媒体 SHA，并使用 `native_edit verify` 回读目标路径、时长和
轨数。六项生产代码离线契约测试通过。对上述真实隔离 edit build 的 CLI
负例在 `existing_edit_publish=false` 处拒绝，未创建输出目录或目标工程；
这一结果只验证失败关闭，不能替代编辑副本的 GUI 生命周期验收。

当前 Build 481 的 `edit publish`、`edit resume-publish` 和正式 `export --build EDIT_BUILD` 均在写入首页或创建输出目录前拒绝。新建草稿的 `publish`/`export` 保持各自已验收的门禁。

2026-09-27 从新建的可丢弃源工程完成正式 build、verify-build、publish 和 verify。
剪映官方 GUI 随后复制此工程，只编辑副本文字为 `Edited via Codex`、
BGM 为 -6.0 dB；保存、完全退出、冷启动重新打开后，设置仍保留。
官方复制副本的 draft ID、名称、目录在首次保存后独立，但 project/timeline ID
仍与源共享。窗口标题、保存位置和进程文件句柄指向副本，源工程冻结的 18 个
文件在每阶段及导出后均未变化。官方 GUI 成片 6 秒、H.264/AAC、180/180 帧，
完整解码通过，抽帧显示标题在计划区间；音频双源拟合的 BGM/视频轨增益比
约为 0.5013（-6.00 dB）。GUI 容器 `major_brand="qt  "`，未做人耳试听，
只能作为官方 GUI 对照。证据在
`work/build481-existing-edit-disposable-20260927/REPORT.md`。这不是仓库
`native_edit build/publish` 的副本验收，正式 `existing_edit_publish=false` 不变。
同一冻结源随后经正式 Skill `edit inspect/build/verify-build` 在新 `work/`
目录构造相同文字与精确 `0.5011872053146362` 音量的离线副本，均通过，
源 18 文件仍未变。离线候选生成新 project ID，官方 GUI 复制却保留源 project ID；
GUI 保存还省略根 fps、默认 1×、默认音量与零起点，并改写媒体路径表达、
当前系统来源和富文本默认字段。完整递归差异见
`work/build481-disposable-edit-structural-20260927/REPORT.md`。这些差异不能
整体忽略，候选还没有 GUI 保存冷重开或正式导出证据。
事务沙箱故障注入确认：edit publisher 在首页索引替换后调用最终
`verify_live` 若失败，目录和索引都已提交，不会自动回滚。因此增加了
编辑副本专用的提交前候选回读：在目标目录放置后、索引替换前核对
draft 身份、完整文件清单、预期时间线、project 引用、四镜像与 inode、
资源/媒体及候选索引身份；失败时保留未登记草稿供检查或 resume，
不会替换首页索引。临时根目录故障注入验证了这个顺序。
Build 481 候选登记还要求全部媒体依赖位于目标副本目录内，路径经解析后
仍须留在副本中；外部绝对路径会在提交首页索引前拒绝。独立可丢弃源的
离线 edit build 两项媒体依赖均位于其目标副本 `Resources/headless-media/`。
这是登记候选的额外约束，不改变已开放版本的路径行为；它不替代提交后
对源工程和媒体的再次核验，也不能消除并发修改的所有窗口。
最终 `verify_live` 仍会在提交后再运行，故不能仅凭此改动临时放开门禁试跑。现在的 edit
`verify-build` 与 live verify 都增加了 `project.json` 的 project ID、主时间线 ID
和唯一 timeline 成员回读，篡改负测通过，但这只强化了身份检查，
`existing_edit_publish=false` 仍保持。
2026-09-28 复测：仓库 73 项单元测试、39 项原生导出守卫测试和
`tools/check_package.py` 全部通过；仓库与已安装 Skill 目录逐文件一致。
已安装入口 `doctor` 确认为 11.4.0 Build 481，运行库和 codec 哈希检查通过，
`existing_edit_publish=false`、`native_export=true`、`native_resources=false`；
`edit --help` 入口可用。这些是守卫及环境检查，并非编辑副本正式导出验收。
同日只读双向比较实验读取全新可丢弃源和官方 GUI 副本的冻结结构，记录
128 条路径差异，仍有 20 条未解释或明确失败关闭；`is_set_beauty_mode=true`
在三个视频材料上由 GUI 新增，现有 `preserved()` 的单向遍历会漏报。
速度、BGM 音量、媒体路径和媒体 SHA 的四项篡改负例均被实验比较器拒绝。
该比较器仅位于 `work/edit-bidirectional-comparator-20260928/`。正式 Build 481
live 回读另加了新增非空字段与字段类型检查，冻结 GUI 副本的
`is_set_beauty_mode=true` 会明确拒绝；它没有接受任何未解释保存差异，
11.4.2/11.5.0 的比较路径不变，`existing_edit_publish=false` 不变。
2026-09-29 只读回放生产 `native_edit.preserved` 与
`reject_new_nonempty_fields` 到冻结的 headless build/官方 GUI 副本：
前者首先拒绝文字 material 的富文本 `content` 字符串差异，后者首先拒绝
GUI 新增的 `is_set_beauty_mode=true`。只在内存中隔离这些差异后，下一处
依次是 `os_version` 保存戳及 segment 单位速度省略。有限负测仍拒绝非单位
速度、非计划音量和未知非空字段；不能用宽泛默认值归一化开门。
完整参数、哈希及路径见 `work/existing-edit-gate-audit-20260929/`。
复核旧隔离 edit build 时还发现：`resource_evidence` 只是 doctor 的证据摘要，
调整图层从 `partial` 收紧为 `unverified` 后会造成原先逐字典比较的运行时
指纹误报。现在只从运行时身份比较中排除这一摘要；应用、Build、Team、库与
codec 哈希、能力位等其余字段仍精确比较。旧 build 再次 `verify-build`
通过，源和首页均未写入。

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

2026-09-26 当前 codec 指纹下又创建一个独立 1× 视频草稿，已安装 Skill
完成 build、verify-build、publish、GUI 保存和冷重开。长草稿名首次因 OCR
换行在身份门失败，第二次在冷重开卡片首次点击无响应时失败；两次原始
记录均保留。校验器加入严格分行拼接与仅限同卡片的单次重试后，第三次
正式 `gui-cycle` 全轮通过，源素材哈希不变，最终应用退出。其后正式 Skill
导出 `isom` H.264/AAC、90/90 帧，完整解码和全帧 OCR 标签 `0…89`
通过；证据见 `work/build481-gui-cycle-headless-regression-20260926/REPORT.md`。
此回归只确认 1× 隔离草稿，不改变编辑副本或非 1× 门禁。

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
已移除的滤镜不恢复；贴纸没有实现证据；调整图层有官方 GUI 2 秒正向输出，但尚无正式 Skill 实现和独立重复验收；复合片段子编辑后结构一致性明确失败；
会员/在线资源不得以缓存存在或技术渲染代替账号和许可证明。原始 STIXGeneral Regular OTF 的旧 GUI 保存样本将字体路径改为应用系统字体，`verify` 因 `Planned font binding changed` 失败；另一个同 SHA 的三轮样本保留结构字段，但缺 UI 字体身份和视觉正对照，见[字体冲突审计](BUILD481-FONT-CONFLICT-20260926.md)。仅其精确 SHA 生成的本地别名已通过，其他字体未验。
原 Skill 从未声明曲线变速支持，因此不是本次 Build 481 会员资源适配项。详见[字体 GUI 验收](BUILD481-FONT-GUI-20260924.md)。
逐帧复核后恒速正式导出仅开放 1×，非 1× 异常及剩余倍率门禁见[恒速补验](BUILD481-SPEED-20260925.md)。

### 复合片段 GUI 隔离实验（2026-09-26）

用已登记的独立 3 秒视频工程，在 Build 481 官方 GUI 中执行“新建复合片段（子草稿）”。首次保存并完全退出后，父草稿、三个子草稿旁文件及组合 ID 一致；冷启动重新打开，时间线显示“复合片段1”，源画面正常。随后进入子时间线将视频缩放从 100% 改为 90%，保存、完全退出、再冷启动打开：子片段面板仍显示 90%，父片段预览保留黑边。官方 GUI 从该冷重开状态导出成功；成片 3 秒、90/90 帧 H.264/AAC、1920×1080/30 fps，所有流 `ffmpeg -xerror` 完整解码，黑边像素、440 Hz 原声频谱及源素材哈希均已检查；未做主观听感验收。

结构验收仍失败：保存后父草稿内嵌 child 为 90%，子草稿旁文件仍为 100%；`combination_id` 与 wrapper 不一致，退出后的三个路径缺 child UUID 目录。`native_compound.check_sidecars` 因此拒绝。官方 GUI 对这份工程能重开和编码，不足以证明可独立复制、可靠编辑或由正式 Skill 构建/导出。Build 481 复合片段生产门禁保持关闭；隔离快照和最小复现见 `work/build481-compound-gui-20260926/REPORT.md`。

该 GUI 成片的 `ftyp` 品牌为 `qt  `，不能当成正式 Skill 的 `isom` MP4 验收。导出后再次退出的草稿仍保留 parent/sidecar 失配，导出本身未修复结构。

2026-09-27 又在 `work/` 的三个完整快照副本中，仅按该已知 90% 编辑同步
父内嵌 child、旁文件 child、`combination_id` 和三个带 child UUID 的路径；
写回精确 Build 481 密文并核对四镜像、解密回读及严格 sidecar 均通过。
随后创建全新 draft/project/timeline/material/segment ID 的独立副本，
把所有原 GUI 工程绝对路径重绑到副本自身资源；旧名称/路径扫描为零，
资源文件、codec、graph 和 sidecar 预检通过。主 agent 使用现有原子首页
登记事务的**隔离实验回调**，仅新增 `Codex-Build481-Compound-Repaired-20260926`
一条首页记录，旧条目顺序及源素材哈希不变。首次尝试启动剪映时系统
报告 Mac 已锁定；后续解锁后继续了 GUI 验收。
这次实验没有修改正式 Skill 的复合片段门禁；过程与恢复记录在
`work/build481-compound-repair-20260926/REGISTRATION-AND-GUI.md`。

同一修复副本随后在三个独立 `work/` helper 进程中导出：三次均有
restore/export 完成事件，输出为 `isom` H.264/AAC、90/90 帧、
完整解码；与官方 GUI 成片对照，边缘黑边一致，三时点全画面 RGB
平均绝对误差约 0.58–0.66，解码音频对齐部分相关系数约 0.999916。
三次的源、登记草稿、旧 GUI 草稿及官方成片哈希前后不变。为使现有
staging helper 接受 Build 481 子稿，实验仅在 `work/` 副本把三个
sidecar 字段中的动态 UUID placeholder 规范化为 helper 已知 token；
正式代码没有修改。修复副本经首页精确标题搜索进入剪映编辑器：
草稿参数显示新标题和目录，时间线含 `复合片段1`，进入子片段后
属性面板可见缩放 90%。再次解锁后由 CUA 保存、返回父时间线、
正常退出并确认主进程消失；保存后完整快照为 43 个文件，原 GUI
测试工程的 50 个文件哈希保持不变。冷启动重开该修复副本，父片段
黑边仍显示，子片段仍显示缩放 90%。修正后的 AX 保存工具在真实
子/父时间线分别完成聚焦窗口标记、目标草稿句柄校验和 PID 定向
Command-S，之前的 1800 节点全树限制不再阻断保存。

**结构验收失败**：保存后 `native_compound.check_sidecars` 拒绝，
明确报错 `Compound sidecar must be in its own draft-local directory`。
剪映官方 GUI 又从冷重开副本导出并显示成功，MP4/MP3 文件位于
本次隔离 `work/` 目录；导出后正常退出，49 文件快照仍在同一
sidecar 路径检查处失败，源媒体 SHA 未变。MP4 为 `qt  `、H.264/AAC、
1920×1080/30fps、90/90 帧、完整解码；与旧官方 GUI 成片的
90 帧 RGB 和 132096 个/声道 AAC PCM 样本逐一相同。独立 MP3
也完整解码，未进行主观听音。成片客观审计在
`work/official-output-audit/REPORT.md`；结构差异在
`work/analysis/build481-compound-gui-save-rewrite-20260927.md`。
GUI 能打开、保留可见的 90% 并导出，不等于 sidecar 可独立复制和
可靠修改，因此不能开放正式 Skill 的复合片段门禁。
三轮日志、逐帧时间戳和视听对照见
`work/build481-compound-helper-trial-20260927/REPORT.md`。

### 调整图层 GUI 最小样本（2026-09-27）

新的隔离 2 秒视频工程在官方 GUI 通过“调节 → 自定义调节”添加 `调整1`，
把红色 HSL 饱和度设为 -50。保存、完全退出和冷启动重开后，界面仍显示
-50；内存解密摘要确认一条 `adjust` 轨、关联的 `materials.hsl` 和一致的
四份活动镜像，源视频 SHA-256 不变。首轮调整层默认长 3 秒，GUI 导出
90 帧且末尾 1 秒空画面，保留为负向样本。随后在官方 GUI 把调整层修剪
到 2 秒，保存、正常退出、冷重开后仍为 2 秒且红色 HSL -50 保留；第二次
官方导出 2.000 秒、H.264/AAC、60/60 帧，音视频完整解码，逐帧无黑尾，
红 ROI 饱和度均值从源的 0.999935 降至 0.694377。

从旧 3 秒快照只改两个时长得到的 work-only 离线候选通过结构检查，
但与最终官方 GUI 2 秒快照有四处差异：HSL 的两条资源路径被剪映迁至
容器内效果缓存，placeholder ID 及 segment material ID 被重生成。
HSL 资源 ID 与已登记 `mask/star` 数值相同，不能据此误用 mask 缓存；
两个真实资源目录的逐文件哈希清单均在该隔离 `work/` 下。

在官方 2 秒冷重开快照的**原始结构**上，又仅为独立沙箱导出实验把媒体和
HSL 缓存的三条路径重绑到按逐文件 SHA 校验的 `work/` 副本。
Build 481 的现有 C++ helper 单次受控调用返回 restore/export 完成事件，
产物为 `isom` H.264/AAC、60/60 帧、约 2 秒，音视频完整解码；
红 ROI 饱和度与官方 GUI 成片的全帧均值相差约 0.00014，末帧无黑尾。
全 60 帧 RGB24 全画面对齐平均绝对误差为 0.472/255；源媒体虽含音频，
本计划视频片段 `volume=0.0`，官方 GUI 和 helper 输出解码 PCM 均为静音，
不能以此证明非静音音频处理一致。
源快照、媒体、缓存和官方 GUI 成片的前后哈希一致。此实验绕开了正式
`build.json`/计划入口，属于 raw GUI 快照的研究证据；正式 Skill 对缺少
受控 build manifest 的旧离线候选已提前拒绝，未生成成片。
从官方快照复制出来的第一版 work-only 计划构造原型虽通过活动四镜像和
材料引用回读，但审查发现它沿用了源 timeline/video/媒体库 ID，保留旧
timeline、`.bak` 和 `.backup` 数据，媒体库时长与路径也未完整重建。
第二版仅在 `work/` 重建了 19 个身份、媒体库和路径，清理旧时间线与备份，
六份镜像和 432 个缓存文件校验通过，六项故意篡改均被拒绝。它仍缺第二份
独立 GUI HSL 样本来确认 `constant_material_id` 的归属，也没有自身的 GUI
保存、冷重开或导出。因此两版都不是可登记草稿或正式离线 build。`doctor` 继续把
调整图层 `offline_build` 记为 `unverified`，仅把单份官方 GUI
冷重开证据记为 `native_reopen=partial`。
`native_export=blocked` 专指正式 helper/Skill 出口；官方 GUI 已有上述一份
正确成片样本。正式 Skill 尚不支持该轨道，三次独立验收未完成。
报告位于 `work/adjustment-layer-gui-20260927/REPORT.md`，单次直接 helper
证据位于 `work/adjustment-layer-gui-20260927/direct-helper-official-snapshot/`；
第二版离线候选与负测在
`work/adjustment-layer-plan-prototype-20260927/candidate-v2/REPORT-v2.md`。

2026-09-28 第二份独立 GUI 隔离工程在保存、正常退出、冷启动重开后，界面仍读回
红色 HSL 饱和度 `-50`，视频与调整层均为 2 秒。运行中只读结构回报显示
两份样本的 HSL `id` 和 `constant_material_id` 各自独立，`resource_id`
与本机 HSL cache 路径一致。2026-09-29 解锁后，剪映主进程经正常退出
消失；退出后 43 文件隔离快照已封存，四份活动镜像密文相同且 inode 独立。
受控 codec 在内存回读确认 HSL `id`、`constant_material_id`、-50 参数、
2 秒时长和 432 文件缓存清单保持；退出时 placeholder ID 被剪映重生，
调整层片段的 material 引用随之同步改写，HSL `extra_material_refs` 仍闭合。
这些证据支持两份官方样本的身份形态，但不能证明 v2 离线候选已被 GUI 接受。
第二工程曾意外创建空时间线02；官方界面删除后中间索引曾将它标记为
`is_marked_delete=true`。当前 `project.json` 与备份只列主时间线，
但时间线02的空目录仍在。因此此样本可作字段身份对照，
不能作为干净单时间线草稿的生产验收。第二份官方 GUI 成片为 2.000 秒、
60/60 帧、H.264/AAC、完整解码通过，红 ROI 饱和度从源 `0.999935`
变为 `0.694403`，60 帧黑像素比例最大为 0，源媒体 SHA 不变。输出仍为
GUI 的 `qt  ` 容器。导出成功后曾因 Mac 锁屏暂停，正常退出和最终快照
已在解锁后补齐。随后再次从首页冷启动打开同一隔离工程，GUI 回读仍显示
视频和调整图层各 2 秒、红色 HSL 饱和度 `-50`；正常退出后封存 46 文件快照，
四份活动镜像一致、HSL 身份和 432 文件缓存保持、源视频 SHA 不变。
本次打开又生成 3 份 `.load.bak`，重生 placeholder ID 并同步改写片段引用；
空时间线02孤儿目录仍在。生产调整图层门禁不变。
隔离证据在 `work/adjustment-layer-gui-second-20260927/`，特别是
`FINAL-EXIT-ADDENDUM.md`、`final-exit-verification-20260929.json` 与
`postexit-reopen-20260929/SECOND-COLD-REOPEN.md`。

`engine/native_adjustments.py` 现提供 Build 481 固定测试素材、2 秒红色 HSL `-50`
的**内存结构实验**：重生 adjust 轨、片段、placeholder、HSL 和 constant ID，
验证引用闭合、源视频 SHA 与 432 文件缓存树。8 项自包含离线测试通过，实际
v2 隔离候选也能作为输入生成双轨图。该模块没有写草稿、首页登记、GUI 保存、
冷重开或正式导出入口；`adjustment_layers` 的 `offline_build` 仍为
`unverified`，生产门禁保持关闭。

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
2× 真 60 fps 输入及微秒边界的十次隔离诊断见
[逐帧速度报告](BUILD481-SPEED-20260926.md)；未改变速度门禁。

2026-09-27 对 2× 的独立只读复核见
`work/build481-speed2-independent-audit-20260927/REPORT.md`：writer 调整只补足帧数，
无法修正每三帧一次的源画面提前；导出副本的源起点增加 1µs 虽在三次
helper 试验中与官方 GUI 的 90 帧标签逐一相同，但改变了源区间，且音频
仍与 GUI 明显不同。它不是生产修复，2× 继续失败关闭。
只用现有 PCM 做的 12 个 250ms 短窗探针发现，0µs 与三份 +1µs helper
音频逐字节相同；helper 相对 GUI 的窗内音调差并非常量，五个窗口无法用
单音模型在 10% RMS 内拟合。它排除了“仅固定时钟偏差加 AAC 头尾裁切”
这一简化解释，尚不能定位 AAC 与变速渲染哪一层出错。方法、输入 SHA 与
逐窗结果在 `work/speed2-audio-nextprobe-20260927/REPORT.md`，门禁未变。
2026-09-28 只读复核进一步核对 AAC 包边界：GUI 与 helper 扣除
skip/discard 后仅差 16 个 44.1 kHz 样本，这不足以解释 2.0–2.5 秒
音频中段的异常；0µs 与三次 +1µs helper 的解码 PCM SHA 完全相同。
下一项可证伪实验是用逐帧标签视频和每 250ms 不同音频标记，分别记录
GUI/helper 的编码前 A/V 时间映射和最终 AAC 包。当前不能把 +1µs、补帧
或 AAC 首尾裁切当作 2× 修复；见
`work/speed2-audio-investigation-20260928/REPORT.md`，门禁仍关闭。
2026-09-29 使用 6 秒、180 个独立画面帧 ID 与 24 个音频频率标记的
新夹具，固定 `[0,6s)` 源区间到 `[0,3s)`、30fps、2×，三次独立沙箱 helper
均输出 `isom`、90 帧、完整解码，输入/seed/helper 哈希前后不变。但逐帧 ID
三次完全相同地出现 `0,2,3,6,8,9,…,177`，恰好 30 个 `k mod 3=2`
位置比理论 `2k` 落后一个源帧。音频 24 个槽中心均可分类，5ms 扫描另有
6 次非单调跳变，严格边界验收未通过。正式 publish 按预期拒绝 2×；
GUI 新建空测试草稿无法通过 Accessibility 可靠放置素材并核对速度，故本轮
没有官方 GUI oracle，不能把上述规律视为已确定根因。隔离报告和逐帧/音频
数据见 `work/speed2-marker-trial-20260929/REPORT.md`；2× 继续失败关闭。

- 独立 `work/` 夹具和验收报告；源草稿与所有输入媒体前后 SHA-256 一致。
- 全部单元测试、源码清单、`doctor`、`build`、`verify-build` 通过。
- 未解释的字段、资源、扩展属性、ACL、身份、回调或输出差异均失败关闭。
- 本地 `work/`、素材、草稿、日志、codec 和官方二进制不得加入 Git。
