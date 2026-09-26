# origin/upstream 与 Build 481 功能差距审计

日期：2026-09-25。以 `upstream/main`、`origin/main`、`codex/jianying-1140-build481`、仓库 Skill 与已安装 Skill 的基线审计为起点，结合本次隔离验收更新。

## 范围与判读

- `upstream/main` 和 `origin/main` 均指向 `344a78f`；工作分支是 `35060a6`，其祖先含 Build 481 适配提交。故本次所谓“上游声明”以 `344a78f` 上的 README、SKILL 和 references 为准，工作分支追加的 Build 481 限定/证据单列。
- 初始基线中仓库与已安装 Skill 的目录内容 `diff -qr` 相同；本次新增 GUI 生命周期入口后再次同步并核对一致。基线 SKILL SHA-256 为 `2bc6ab17…e6b8474f3`，后续内容变更须以当前包检查与 `diff -qr` 为准。
- `有代码/测试` 仅说明存在序列化、验证器、测试或实验路径，不等于上游承诺或 Build 481 正式能力。Build 状态用“构建、GUI 保存/冷重开、正式导出/输出、资源许可、门禁”分别判断。运行版本必须是精确 11.4.0 Build 481 及匹配签名、库和 codec。
- Build 481 的 `native_export=true` 不代表资源总门禁打开；`native_resources=false`。被逐项验收的资源仅由精确 key/SHA 的单项门禁放行。矩阵依据 [资源矩阵](BUILD481-RESOURCE-MATRIX.md#适配范围与证据) 与 [分阶段验收](BUILD481-VALIDATION.md#当前结论)。

## 用户功能清单逐项核对

状态缩写：`构建`=离线 build/verify-build；`重开`=剪映 GUI 保存、退出、冷启动复开；`导出`=正式 Skill export 并检查容器/帧数/完整解码；`许可`=技术命中资源不代表账号、商用或再分发权。

## 当前交付分层

以下分层只对表中明确写出的素材、参数、资源 ID 和版本指纹成立，不推广为剪映全部能力。

| 层级 | Build 481 结论 |
| --- | --- |
| 已完整支持（在本次验收样本范围内） | 隔离草稿创建、首页登记、结构检查；基础 H.264 视频、普通文字、本地 WAV 的三次独立原生导出；所列单项媒体与组合媒体的构建、GUI 保存冷重开、正式导出及抽样视听/频谱检查。 |
| 已支持但有参数限制 | 仅 1× 正式速度导出、四个固定字体 SHA、声明的线性关键帧通道、六个固定几何蒙版、固定叠化、固定轻微抖动、本地 MP3/WAV/PNG/JPEG/GIF/HEVC。每个单项的确切约束见下表。 |
| 仅 GUI 支持 | `gui-cycle` 对已登记、含本机资源文件的 Build 481 新建隔离工程恢复，1× 与 2× 各三轮身份回读、保存、正常退出与冷重开通过；另有保存前错误目标拒绝。工具现能识别 `jy14-edit-build/v1` 的离线记录及验证器，但 `existing_edit_publish=false` 在启动 GUI 前阻断，编辑副本未获 GUI 验收。它只提供生命周期证据，2× 导出和高级效果仍按各自门禁关闭。 |
| 仅离线构建支持 | 已有草稿独立副本的 inspect/build/verify-build；复合片段的递归构建与冻结快照导出是 11.4.2/11.5.0 历史实验，不能视为 Build 481 构建成功。 |
| 当前失败关闭 | Build 481 编辑副本首页登记及正式导出、所有非 1× 倍率、曲线变速、任意未验字体、额外转场/特效、滤镜、花字、贴纸、调整图层、复合片段正式登记、泛化会员/在线资源。 |
| 原 Skill 本身没有承诺 | 曲线变速、贴纸、调整图层、任意在线/会员资源；更多转场和特效也没有“全部资源”承诺。花字/滤镜曾有旧代码，但当前发行已明确移除。 |
| 需要会员或在线资源 | 若某资源由官方 GUI 标为会员或在线，必须在当前账号正常获得、拥有对应本机缓存和权益，再逐 ID 验收；当前没有因此额外开放任何资源。 |
| 目前无法可靠实现 | 复合片段原生保存后的子草稿引用、2× 末帧映射、原始 STIX Regular 字体绑定及没有可回读状态的任意 GUI 控件；现阶段均保留失败关闭。这里表示尚无可靠实现，不断言未来不可能。 |

| 功能 | 上游：声明 / 代码但未承诺 | Build 481：构建；GUI 保存/冷重开；导出/结果 | 门禁与未完成原因 |
|---|---|---|---|
| 草稿创建 | 明确承诺生成可编辑原生草稿；有 build/schema/profile 实现与测试。 | 通过；视频、文字、音频、资源等隔离工程均建成，基础类别均在 GUI 保存冷重开。 | `draft_create=true`。非支持字段拒绝；空轨草稿仅离线构建，未原生验收。 |
| 首页登记（publish） | 明确承诺 publish 是本机首页登记；有 staging、索引与恢复实现/测试。 | 通过三次真实登记、GUI 播放保存、正常退出、冷重开与 `verify`；这是本机登记，非线上发布。 | `publish=true`。Build481 非 1× 倍率在写首页前拒绝；macOS provenance/macl 已明确处理，保留身份和素材检查。 |
| 检查（verify） | 明确有 doctor、verify-build、verify；相应身份、媒体引用、文件/hash、镜像测试存在。 | build 回读、publish 后 live verify 通过；资源逐项按其证据层验收。 | `verify=true`。结构检查不替代画面/声音判断。 |
| 独立副本编辑 | 明确承诺在副本中编辑、不覆盖源；`native_edit` inspect/edit/build/publish 有实现和测试。 | 文字替换、音量修改副本离线 build 通过，历史实验曾登记且源字节不变；旧样本 `verify-build` 仍通过。新隔离 build 已将构建时 runtime 身份嵌入记录，当前离线验证通过，篡改 codec SHA 的负测被拒。`gui-cycle` 编辑 schema 适配器的六项生产代码离线测试通过，真实编辑 build 在 GUI 前被当前门禁拒绝且未创建目录。GUI 冷重开只有首轮历史记录；在当前 macOS 26.6.2 上，严格 live verify 拒绝 OS stamp、三个默认 `speed=1` 和根 `fps` 的保存差异。尚未证明严格 live verify 或标准 MP4 输出。 | `existing_edit=true` 仅允许离线 inspect/build/verify-build；`existing_edit_publish=false` 阻止 Build 481 编辑副本登记和正式导出。仅单时间线/无云身份/不含复合片段、转场、滤镜、蒙版；系统默认字体。原生默认字段变化须逐项验证，不能直接放宽全结构比较。 |
| 视频（H.264） | 明确声明本地视频；参考限定单视频流、最多一音频流，拒旋转元数据/未知像素格式。 | 构建、GUI 保存/冷重开通过；基础视频 3 次 helper 加 Skill 正式出口复验。90/90 帧、H.264/AAC、isom、解码通过，画面可见。 | 基础 native export 开放。未覆盖所有编码、帧率与资源交叉组合。 |
| HEVC | 上游明列输入白名单；代码按媒体 codec 识别。 | 单项 build、verify、90/90 正式导出/解码通过；与其他五类素材的组合草稿 GUI 冷重开，预览可见。组合另经正式 Skill 导出，360/360 帧、isom、完整解码并抽帧检查。 | 基础媒体门禁范围内；其他编码参数组合仍未穷举。 |
| PNG / JPEG | 上游明确支持图片轨，代码登记并保留原文件；静态图不得设源偏移或非 1x。 | 两者各自 build、verify、单项正式导出 90/90 解码通过；与 GIF/HEVC/MP3/WAV 组合 GUI 冷重开且预览可见；组合已另经正式 Skill 导出 360/360 帧并完整解码。 | 基础媒体门禁范围内；全格式组合、不同画幅等未穷举。 |
| GIF | 上游明确支持 GIF；按实际容器时长，不允许超出动画实际时长循环延长。 | build、verify、单项正式导出 90/90 解码，三时点抽帧有动画变化；独立 GIF 与六素材组合 GUI 保存冷重开，画面可见/变化。组合已另经正式 Skill 导出 360/360 帧并完整解码。 | 基础媒体门禁范围内；文档记录曾在 11.5.0 遇到 149/150 间歇缺帧，Build481样本通过但没有证明问题根因消失。缺帧按严格帧数 gate 拒绝，不补帧/重试。 |
| MP3 / WAV | 上游明确将独立音频用于本地 BGM/音效；音量字段有实现。 | 各自 build、verify、90/90 正式导出/完整解码；组合草稿 GUI 冷重开并正式导出 360/360 帧，1 秒和 4 秒各有 220 Hz 主峰，7 秒无计划音轨时静音；无主观听感验收。 | 可用；不承诺响度线性映射：WAV 计划 volume=0.5 实测增益约 0.352；听感仍需逐片检查。 |
| 文字 / 字幕 | 明确承诺可编辑字幕、标题，含字号/坐标/颜色/描边/字体路径字段；渲染与验证代码存在。 | 普通文字 build、GUI 保存/冷重开、正式原生导出通过；90/90，抽帧文字可见。 | 基础文本可用。不同布局/emoji/多行需逐片验；退役花字不在此范围。 |
| 本地字体 | 上游声明独立静态 OTF/TTF、hash 入草稿及双绑定验证；拒绝字体集合、可变/在线字体。 | Monaco、固定 SHA Arial TTF、STIXGeneralItalic OTF 和显式生成的 Regular 别名分别 GUI 保存/冷重开、绑定回读、字体字节校验及正式导出通过。历史 42pt 原始 Regular OTF 保存后改绑系统字体；导出前能渲染但 GUI verify 失败。解锁后的另一份 12pt `STIX 123` 隔离草稿三轮保存/冷重开均保留原始 Regular SHA，四镜像和源素材 SHA 相同，原始 JSON 差异归一后无实质变化；GUI 预览与 STIX/Arial 导出帧的比较缺已知 GUI 正控制，视觉身份仍不确定。 | Build481 仅四个精确 SHA 放行；原始 Regular 与其余字体关闭。字体文件可用/缓存命中不证明授权。 |
| 关键帧 | 明确声明线性关键帧；视频 x/y/scale/rotation/opacity/volume、文字 x/y/scale/rotation、音频 volume。`native_motion` 生成/校验，测试验证点序和曲线。 | 原承诺通道均覆盖（九通道主样本及文字 y/rotation 单项）；GUI 保存冷重开、verify、正式 Skill 导出通过，画面运动可见。 | 精确线性通道开放；要求 speed=1、source_start=0；裁切入点/变速映射、非线性、蒙版关键帧拒绝。 |
| 恒速 | 上游计划格式写 0.1–8x 恒速，代码将 speed 序列化；边界值可 build 不等于导出承诺。 | 历史六档 0.1/0.5/0.75/1/1.5/8x 曾构建、组合 GUI 冷重开并以抽样时间码和完整解码验收；逐帧复核又发现 8x 与计划采样映射不符，0.1/0.5x 末帧越过源范围右边界。2x 有 89/90 帧反例，90/90 文件亦每第三源帧落后一格，且不同于官方 GUI；0.75x 混速样本末帧越界，1.5x 有映射偏差候选，均缺独立单倍率对照。1x 正式出口另经 Vision 90/90 全帧验证，源标签严格 0…89；2x/60fps work-only 三次 180/180 全帧连续，后续官方 GUI 60fps 对照为 179/179 帧、时码 0…178，末帧数仍不一致。 | 当前仅开放 1x 正式登记和导出，所有非 1x 倍率均失败关闭。帧数与少量抽帧不足以证明逐帧正确；音质无主观验收。 |
| 曲线变速 | 原 SKILL / reference 未声明曲线变速；代码仅支持标量 speed 与线性关键帧属性，不存在 speed 曲线计划语义。 | 隔离草稿可由 AX 打开曲线页并由 Vision 识别 8 个预设；校准后两次动态点击“蒙太奇”都未改变“无”的选中边框，冷重开解密仍只有默认 1×，未获非空曲线样本；无导出验收。 | 明确不支持；不是已承诺功能的回归。预设无 AX 语义身份/可回读选中状态，需可靠官方样本、计划格式、时间映射和输出验收。 |
| 几何蒙版 | 上游声明六种静态形状 circle/rectangle/line/mirror/star/heart 与位置、尺寸、旋转、羽化、反转、矩形圆角；依赖本机固定资源身份。 | 六项均 build/verify，官方 GUI 选中后保存冷重开，ID/路径/逐文件 SHA/tree hash 核实；六个正式 Skill 导出各 90/90、isom、解码通过且抽帧正确。圆形另有完整 publish/verify。 | 六个精确资源 key 开放；总 `native_resources=false`。无自定义/文字蒙版与蒙版关键帧，缓存回指意味着依赖原机资源。 |
| 转场 | 上游明确支持主视频相邻片段的 `dissolve`，偶数帧、素材 handles / repeat-edge 审计；其他转场未接入。 | `dissolve` Build481 GUI 资源应用、保存冷重开、verify 与缓存 hash 核对；三次 helper + 正式 Skill 导出 168/168 isom，抽帧过渡可见、完整解码。 | 只开固定 `transition/dissolve` 身份；其他转场关。原声同相重叠约 +6.03dB，输出仍须检查真实音频。许可不能由渲染推断。 |
| 特效 | 上游本地资源机制有代码；发行计划现明确采集效果为 `light-shake`，固定参数和包身份。 | 轻微抖动 GUI 应用、保存冷重开、资源包与编译缓存 hash、正式 build/publish/verify、正式导出 90/90 isom 解码通过；逐帧对照可见位移。 | 只放行 `effect/light-shake` 的固定资源与参数。别的效果关闭。UI 显示可商用不等于账号或再分发许可。 |
| 滤镜 | 代码过去/通用资源机制涉及 filter；当前 Skill 明确移除高清黑白滤镜。 | 退役 filter 会报错。本机另有候选 `7460040331627598345` 的完整缓存包，但官方 GUI 未能确认同一材料可见，未应用、保存、冷重开或导出。 | 当前关闭；不能把缓存包或“非会员”目录字段当作可用/授权证据。测试覆盖拒绝旧计划。 |
| 花字 | 当前 Skill 明确移除橙色描边花字；普通文字与自定义颜色/描边仍受支持。 | 退役 text-effect 被代码/测试拒绝；无 Build481 花字保留验收。 | 不属于当前支持项；不静默降级移除。 |
| 贴纸 | 上游新计划未接入；`resource_evidence` 为独立类别，存在拒绝/门禁描述，不是已支持承诺。 | 未有 Build481 build、GUI保存冷重开、导出/输出正确或资源身份验收。本机扫描到的 `InfoSticker` 类型包对应花字纹理或文字效果，不能当作独立贴纸。 | 关闭；原因是没有可确认身份的独立贴纸包、完整持久化及输出证据。 |
| 调整图层 | 上游新计划未接入；可见于证据/能力名称，不构成支持承诺。 | 2026-09-26 隔离基线单视频 build/verify-build 通过；`adjustment` 和 `adjustment_layer` 两种候选轨道均在计划白名单拒绝且未生成草稿。暂无可确认的 GUI 调整图层样本、冷重开或导出证据。 | 关闭；缺原生节点结构、资源依赖和持久化验收。最小复现在 `work/adjustment-layer-audit-20260926/`。 |
| 复合片段 | 上游有 11.4.2/11.5.0 实验代码，可离线递归检查/编辑/冻结快照导出；文档明示不能可靠交付为可编辑嵌套草稿。 | `native_compound.py` 的 `SUPPORTED_PROFILES` 不含 Build 481，蓝图也固定 11.4.2，故本版本生产离线复合构建未开放。历史版本保存时子草稿引用变根路径、缺 ID，GUI 持久化失败/`publish` 被拦截。只读扫描 36 份本机 Build481 隔离草稿没有原生复合样本；work-only 将 11.4.2 蓝图身份改为 481 后，用当前新 codec 构建的合成图通过 strict `verify-build`，故受保护目录阻塞并非此离线结构的唯一问题。刻意破坏 child `project_id` 的负向对照被 sidecar 校验拒绝。未在 Build 481 GUI 打开、保存、冷重开或导出。 | Build 481 生产全路径阻断。先取得本版本官方样本，解决原生保存/sidecar 引用重写，再逐层验收；旧模板合成结构与静态符号都不构成格式兼容证明。隔离记录在 `work/build481-compound-strict-verify-20260926/`。 |
| 音频处理 | 上游支持片段 volume 0–4、线性 volume keyframe、本地音轨；没有保持音高计划字段。 | 基础音轨 build/GUI 保存冷重开/正式导出通过；关键帧 volume 通过；MP3/WAV 有频谱证明信号。混音响度、变速音质及任意音量感知未验。 | 已声明的基础音量与关键帧可用；不声称保持音高/压限/淡入淡出或响度校准。叠化音频会重叠。 |
| 导出参数 | 上游明确提供原生 MP4 导出；CLI 有 bitrate、timeout，构建设置包含画幅/fps/编码；数值范围不等于矩阵全覆盖。 | 基础及固定子集导出为标准 H.264/AAC `isom`，帧计数、ffmpeg 完整解码、代表画面检查通过。还没有把所有尺寸/fps/bitrate/硬件编码组合逐一验收；GUI 输出可能是 `qt  `，不作为 MP4 证据。 | Build481 `native_export=true`；严格检查标准容器、帧数。输出目录须新建；未验组合保持拒绝或不宣称支持。 |
| 会员 / 在线资源 / 在线模板 | 明确不在发行范围；无登录、自动下载、伪造身份/授权路径。资源目录可验证已本地取得的固定字节，这是代码存在而非获取权限承诺。 | 叠化/轻微抖动按官方 UI 获得固定包后实测；其他会员/在线资源没有加载、构建、重开或导出验收。用户账号等级未验证。 | Profile 层 `member_online_resources` blocked；不支持任意会员资源、在线模板或权益获取。资源技术可渲染≠用户权益/许可。 |

## 最有价值的下一步缺口

1. **先处理声明范围内的恒速 2× 帧数或源末帧错误，再考虑扩大速度范围。** 原 Skill 公开写明 0.1–8x 恒速，Build481 当前仅开放 1×；2× 的 3 秒零入点样本曾为 89/90 帧，重新同步后的三个同语义样本虽为 90/90，末画面仍早于 GUI 一个源帧。两组 staging JSON 在 UUID/路径规范化后相同，当前没有可证因果。writer0/加微秒候选也破坏容器或时长/源入点条件。必须同时满足 `isom`、90/90、正确源末帧和目标时长，才能更新精确倍率门禁。
2. **补齐组合媒体的声音听感与更广参数。** 六格式各自单项导出、组合 GUI 冷重开及组合正式导出均通过，组合画面与两段音轨的客观频谱已检查；主观听感和更多编码、画幅、帧率组合仍待验。
3. **复合片段持久化属于较大的产品能力缺口。** 11.4.2/11.5.0 的代码和冻结快照出口存在，但历史 GUI 保存发现嵌套 child path/ID 损失并被 publish 门禁拦截；Build 481 尚未有本版本的材料采集和离线构建。由于原文把它限定为实验能力，优先级低于已经明示恒速范围的 2× 修复。

曲线变速、贴纸、调整图层、在线模板等属于从未承诺/当前明确不支持项目，只有在产品范围扩展后才应立项，不应混写为 Build481 适配回归。滤镜和花字已经主动退役。

## 关键证据链接

- [上游 README](https://github.com/mcncarl/jianying-headless/blob/344a78f/README.md)、[上游 Skill](https://github.com/mcncarl/jianying-headless/blob/344a78f/skills/yichen-jianying-edit/SKILL.md)、[计划格式与媒体/运动/资源约束](../skills/yichen-jianying-edit/references/headless-macos.md#jy14-headless-planv1)、[上游导出说明](../skills/yichen-jianying-edit/references/export-macos.md)
- [Build481 资源矩阵](BUILD481-RESOURCE-MATRIX.md)、[分阶段验收](BUILD481-VALIDATION.md)、[媒体与组合验证](BUILD481-VALIDATION.md#媒体格式补验-2026-09-24)、[GUI 冷重开](BUILD481-GUI-REOPEN-20260924.md)、[2x 恒速矩阵与诊断](BUILD481-SPEED-20260925.md)、[复合片段限制](../skills/yichen-jianying-edit/references/edit-existing-macos.md)
- 核心代码位置：`engine/runtime_profiles.py`（capability 与三层 evidence）、`engine/native_motion.py`（关键帧/蒙版）、`engine/native_effects.py`（叠化）、`engine/native_visual_effects.py`（视觉效果）、`engine/native_resources.py`（精确资源 key/hash）、`engine/native_compound.py`（复合图/持久化检查）、`engine/native_export.py`（导出白名单与输出验证）。

## 已放行的本机资源身份

下表中的缓存根均为当前用户 `~/Movies/JianyingPro/User Data/Cache/effect/`。
逐文件相对路径、大小和 SHA-256 清单记录在
[native-resource-catalog.json](../engine/native-resource-catalog.json) 的对应 `resources` 条目；
正式构建会逐文件核对，目录存在本身不构成许可。

| 资源 key | 官方材料 ID | 缓存根以下目录 | tree SHA-256 |
| --- | --- | --- | --- |
| `mask/circle` | `7356934080102928946` | `82432977/3ab1c47350d987c8ad415497e020a38b` | `755f487494e041e0adceaff3c1a747b1238773c071fe3297d1911112cccd3946` |
| `mask/rectangle` | `7356934318301647410` | `82432980/02b8999168d121538a98ea59127483ef` | `c8d500f2840e387e372744f6f44e1d2128e29c94df3dc482cf18a8de7d2f0ec6` |
| `mask/line` | `7356933362960831003` | `82432976/4c6a0ef5de6a844342d40330e00c59eb` | `e548c277fb2a6e06739855160a985a676221b19e9c4a65b60c8d75df1aea3c29` |
| `mask/mirror` | `7356933823327638042` | `82432979/95ac211c99063c41b86b9b63742f4a6d` | `36365677e9ef362fdba0a5a9169cd9427c85f3ebecfc16f98c7d17a21bef3977` |
| `mask/star` | `7416258989467374091` | `83244852/7ff81ba985da9aae07b69c5b77ea7e9a` | `ba3fd7ebd571eba4f3383343eb7b8f6f504dfef8d6477af3bbe49bd8c67f2a8e` |
| `mask/heart` | `7416258912162157068` | `83244815/27ae3c55bb97e470a75f61a8d34832bf` | `d72134d8c23f46d9d2ca3b2d7171908285487f2a1cb69cdb57593d427e422936` |
| `transition/dissolve` | `6724845717472416269` | `6724845717472416269/33d3a1ad16e89a4e2c9b6d45e3ec7aa1` | `dc006fa499721070ec74f98a2aa01ca7baa85bca5a7145b12acf6c4cdc0243da` |
| `effect/light-shake` | `7399493554147527951` | `7399493554147527951/f443ba63a627600bf408d3ed98fe788e` | `109b61dbbfb2f09a69e01e56197d840f7199f6ad51201b0b62a1bc2341929555` |

普通媒体和本地字体没有剪映在线资源 ID：媒体按本次输入文件 SHA-256 与草稿副本核验，
字体按 `engine/native_export.py` 的四个精确 SHA 门禁。未放行的资源没有可作为正式
Skill 输入的 Build 481 身份清单；GUI 会员可见性也不自动改变门禁。

## 未放行候选的停止记录

本机滤镜候选 `7460040331627598345`（缓存目录
`effect/7460040331627598345/f332e2f20de168f57e6814d22698f423`）有
447 个文件、2,530,966 字节，tree SHA-256 为
`5e91c028b5188428ea43bc27b5ba89d8c4948ea8d4bd444111d07c6c7ea8a929`。
逐文件清单在忽略目录
`work/build481-extra-resources-20260925/filter-candidate-manifest.json`。
缓存目录字段标为非会员，但剪映 11.4.0 Build 481 官方滤镜界面没有可靠显示该
材料身份，搜索框也没有可靠接收输入；隔离工程因此停在应用前，没有保存持久化或
导出验收。该候选**不在**上方已放行表，也不进入正式 catalog。

另有静态审计候选「智能美颜 → 美白」ID `7408076966890425615`，本机 panel 缓存
把它列于 category `5913983`；对应资源包 16 文件、244,421 字节，tree SHA-256
`122bde662d18ec613a9af2b607c089f3f8dd6e35bd5aabf34275274aac120f9e`。
逐文件清单在忽略目录 `work/build481-effect-audit-20260925/candidate-manifest.json`。
此资源依赖人脸与肤色分割模型，当前项目没有对应材料类型、轨道绑定和参数实现；
本轮没有 GUI 可见性、账号权益、保存或导出证据，因此它也是**失败关闭候选**。

本机转场面板缓存只读盘点找到 124 个唯一转场 ID，但分类响应只保留首 50 条，
且本地效果缓存中只有 `transition/dissolve` 具备完整可核验包。`云朵`
`6955722927161479694` 与 `闪黑` `6724239388189921806` 没有本机包，
未从面板参数推断材料 schema，也未尝试绕过官方获取流程。清单与逐文件哈希在
忽略目录 `work/build481-transition-audit-20260925/transition-index-audit.json`；
因此目前不能增加第二个转场的 Build 481 正式门禁。

又在官方 GUI 新建两段视频的独立草稿尝试“云朵”：AX 能读回搜索词，真实键盘
和粘贴输入后只有建议词，没有可确认的结果卡或精确资源 ID；选择建议也未改变
卡片列表。保存、正常退出、冷重开后解密草稿仍无转场材料，四镜像一致，源素材
SHA 未变。本机完整 Cache 只读清单覆盖 18,087 个文件，目标 ID 只在一条缓存
HTTP 响应中出现，效果包仍不存在。这不能判断账号权益，只能判断本次未能应用并
验证该资源；证据在忽略目录 `work/build481-transition-cloud-gui-20260925/REPORT.md`。
