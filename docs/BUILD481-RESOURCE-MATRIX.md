# Build 481 资源功能专项矩阵

本页只记录精确剪映 11.4.0 Build 481 的资源功能边界与可复核离线证据。
代码单测、字段序列化或另一剪映版本的缓存捕获均不能替代 Build 481 的
原生打开、保存冷重开和原生导出验收。总门禁 `native_resources=false` 保持有效，
直到各项证据分别通过。

## 适配范围与证据

| 功能 | Skill/核心项目支持范围 | Build 481 当前证据 | 结论 |
| --- | --- | --- | --- |
| 基础本地媒体与剪辑 | 本地 H.264/HEVC 视频、PNG/JPEG/GIF 图片、独立音频/BGM/音效、画中画和恒速剪辑 | 基础视频、普通文字、本地 WAV 各完成三次隔离原生导出；每次进程和完成事件成功、90 帧/3 秒、H.264/AAC、完整解码，源草稿和 staging 输入哈希不变。恒速门禁仅允许 0.1x、0.5x、0.75x、1.0x、1.5x、8x；曲线变速仍关闭，2x 有 89/90 帧反例，见[恒速补验](BUILD481-SPEED-20260925.md)。PNG/JPEG/GIF、HEVC、MP3/WAV 六类另完成逐项隔离构建与导出；GIF 单项和六素材三轨组合草稿已在 GUI 保存冷重开，组合 `verify` 四镜像相同、源文件未变，实际预览可见图片、GIF 动画和 HEVC。组合未另行导出、未记录主观听感，详见[媒体格式补验](BUILD481-VALIDATION.md#媒体格式补验2026-09-24)。尚未遍历全部媒体与特效组合 | Build481 基础视频/文字/音频及已验收的六档恒速可用；其他速度、未覆盖媒体/资源组合不视为已验收 |
| 普通字幕 | 可编辑文字片段；样式、描边和位置按计划字段生成 | 普通文字离线构建为 `verified`；本机默认文字轨三次原生导出通过，隔离工程已在 GUI 保存和冷重开。整合 keyframe 样本使用 Monaco 静态 TTF，helper 和正式 Skill 输出中可见单宽字形，其隔离工程也已保存冷重开 | 普通文字基础原生导出已验证；Monaco 的单项正式导出已通过 |
| 本地字体 | 静态独立 OTF/TTF；复制到草稿并校验字节和富文本绑定。拒绝字体集合、可变字体及带账号/授权身份的在线字体 | Monaco TTF（`e110b2fb…85c028`）、Arial TTF（`52597982…fd2bd9`）及 STIXGeneralItalic OTF（`7f6bf9ca…319a72`）各自通过隔离草稿 GUI 保存、冷重开、绑定回读、字体字节校验及正式 Skill 导出。原始 STIXGeneral Regular OTF（`5add3f3f…5357a7`）保存后改绑系统字体；显式本地别名工具在不改源的前提下生成固定 `154e149b…47a0717` OTF，该别名通过 GUI 冷重开、双绑定回读和正式 Skill 90/90 帧导出 | Build 481 正式导出仅放行四个精确 SHA；原始 Regular 和其他未验字体继续阻断。Italic 与 Regular 别名样片静音，不作为音频听感证据 |
| 关键帧 | 线性曲线。视频通道 `x/y/scale/rotation/opacity/volume`；文字通道 `x/y/scale/rotation`；音频通道 `volume`。至少两个有序采样点，首点从片段 0 开始。裁切源入点和变速时间映射拒绝 | 整合样本覆盖视频六通道、文字 `x/scale`、音频 `volume`，九通道通过 build/verify-build、三次隔离 helper 原生渲染、GUI 保存冷重开与 verify 回读，正式 Skill 再导出一次，画中画运动可见。独立默认字体样本的文字 `y/rotation` 三次 helper 导出、正式 Skill 导出、画面抽帧、GUI 保存冷重开与 verify 回读均通过 | 原 Skill 声明的线性关键帧通道按精确节点形状与 1x 时间映射正式开放；非线性插值和裁切/变速关键帧仍阻断 |
| 几何蒙版 | 仅视频素材；circle、rectangle、line、mirror、star、heart 六种形状；支持尺寸/位置/旋转/羽化/反转，矩形可圆角。线形蒙版不接受宽高，蒙版关键帧未接入 | 六种形状分别通过 work-only helper 导出，并各由 Build481 GUI 官方选用、保存、冷重开，资源 ID/路径/逐文件 SHA 与固定清单一致。六项又分别通过正式 Skill `build`、`verify-build`、原生导出、90/90 帧完整解码及抽帧画面；圆形正式草稿额外完成 `publish`、GUI 冷重开及 `verify` | Build481 六种几何蒙版按精确资源 key 正式开放；不扩展到自定义/文字蒙版或蒙版关键帧。`native_resources=false` 总门禁不变 |
| 叠化转场 | 仅主视频轨相邻片段；偶数帧时长，两端须有源素材余量；端点重复帧须显式选择并审计 | Build 481 官方 GUI 选用资源 `6724845717472416269`，保存、完全退出、冷重开并播放核验；固定 tree SHA `dc006fa499721070ec74f98a2aa01ca7baa85bca5a7145b12acf6c4cdc0243da`、14 文件。GUI 导出为 QuickTime `qt  `，不作为标准 MP4 证据；之后三次 helper 与正式 Skill 导出均 168/168 帧、`isom`、H.264/AAC、完整解码 | Build 481 仅固定 `transition/dissolve` 子集开放；不开放其他转场。保留叠化音频重叠警告 |
| 轻微抖动 | 核心代码识别 `light-shake` 和 `range`/`speed` 参数；Build 481 只接受精确捕获包与已声明参数边界 | 官方 GUI 选用、应用、保存、冷重开；27 个源文件 tree SHA `109b61dbbfb2f09a69e01e56197d840f7199f6ad51201b0b62a1bc2341929555`；含两份 macOS 26.6.2 编译缓存的 29 文件完整目录 tree SHA 为 `7f18f41e811c40c98161accd3865e2832ec8af3b5cfafc847446c6b3446777c6`。正式 Skill build/verify-build/publish、GUI 冷重开、verify、helper 画面对比和 Skill 导出均通过，90/90 帧、`isom`、H.264/AAC、完整解码 | Build 481 仅固定 `effect/light-shake` 子集开放；其他特效仍失败关闭。账号权益和商用/再分发许可未由渲染结果证明 |
| 滤镜与花字 | 当前发行已移除高清黑白滤镜与橙色描边花字；普通文字颜色与描边仍可用 | 代码测试拒绝退役资源，不会静默降级 | 按已移除处理，不作为待适配 Build 481 功能 |
| 贴纸、调整图层、复合片段 | 没有可用于本次 Build 481 资源适配的完整声明支持 | 没有该版本离线资源及原生持久化证据；复合片段冷重开门禁关闭 | 不计入当前 Skill 的 Build 481 已支持范围 |
| 会员/在线资源、在线模板 | 不属于离线 Skill 发行的受支持资源；不得绕过账号权益、伪造许可或移除身份字段 | 本次仅通过剪映官方 GUI 正常获取已验的叠化和轻微抖动本机资源；未验证会员等级或其他在线资源，Profile 标为 blocked | 不纳入任意在线资源适配，也不把缓存命中视为使用许可 |

矩阵状态顺序为 `offline_build / native_reopen / native_export`。这里的“离线专项通过”
只代表本页明确写出的代码/数据检查，不会将 Build 481 Profile 的证据层自动升级。
Build 481 基础 `native_export` 已开放并通过视频、普通文字和 WAV 各三次导出；
`native_resources=false` 总门禁保持关闭。经单项证据确认的 Monaco、Arial TTF、STIXGeneralItalic OTF 与显式生成的 STIXGeneral Regular 别名、
线性关键帧通道、六种几何蒙版、固定叠化资源 `transition/dissolve` 和轻微抖动资源
`effect/light-shake` 由独立精确门禁开放；其他转场/特效与资源仍没有 Build 481 正式验收。
Skill 范围内的基础媒体类型、BGM/音效、画中画和变速并不代表每种素材、编码和资源的
交叉组合都在 Build 481 上通过；未列出的组合须按具体计划补验。

## 本次离线检查

结果保存在 `work/build481-resource-audit-20260924/`：

- `offline-build.json`、`offline-combined-verify.json`：精确 Build 481 的隔离构建和结构
  回读通过；4 秒、4 轨、3 个媒体文件、1 个 Monaco 字体文件，含本地音频、字幕、画中画
  视频和 7 个线性关键帧通道。`live_written=false`，未登记首页。
- `all-keyframes-build.json`、`all-keyframes-verify.json`：相同隔离计划补齐视频透明度和音量
  动画后重新构建与回读；视频六通道、文字两通道、音频音量共 9 个关键帧通道通过。
- `font-tests/result.json`：本地 Monaco TTF 的 41 项单测通过；单测使用测试替身，
  没有启动原生渲染器。
- `keyframe-tests-final/result.json`：隔离 keyframe fixture 的 10 项单测通过。
- `all-mask-checks.log`：六种几何蒙版均通过字段序列化/结构回读；没有复制系统缓存。
- `mask-transition-checks.log`：叠化的 12 帧时长和素材余量审计通过；叠化及轻微抖动
  的材料构造因资源清单缺少 `tree_sha256` 被拒绝。
- `visual-tests.log`：现有专项有 8 项通过，1 项轻微抖动材料绑定失败，原因同上。
- `focused-tests.log`：第一次尝试未设置 `PYTHONPATH=engine`，仅发生导入失败，没有执行测试用例；
  它不作为验收结果。

本轮曾在 `engine/native_export.cpp` 更新期间由 CLI 按源码身份门禁停止；待代码与 pin 同步后，
已重新运行精确 Build 481 的离线整合 build/verify-build 并通过。没有绕过正式资源哈希门禁，
没有写剪映首页或全局草稿。基础视频/文字/WAV 原生导出已各通过三轮；恒速仅开放
0.75x/1.0x/1.5x，曲线速度仍阻断。整合字体与关键帧样本已完成剪映 UI 保存冷重开；
文字 `y/rotation` 独立样本的 GUI 冷重开已完成；Monaco 字体与已验线性关键帧通道
已有正式 Skill 出口证据。以上是本轮追加验收前的历史状态：当时转场尚无 Build 481 捕获，
轻微抖动材料绑定失败。后续逐项证据见下方“Build 481 叠化与轻微抖动正式验收”。
当前 `native_resources=false`，未验资源能力的正式导出 gate 仍关闭。

2026-09-25 又用 `work/native-mask-test-20260925/fixture/` 中独立构建的 12 秒、
六蒙版单素材 fixture 跑完 `engine/test_native_masks.py`：16/16 通过，
`verify-build` 为 `verified`，结果记录在
`work/native-mask-test-20260925/test-work-fixed-1/result.json`。
该 fixture 不随源码分发；专项测试修正了对 `prepare()` 的 catalog 模拟接口和
异常消息大小写，保留了缺文件、篡改和符号链接失败关闭以及源缓存未变的断言。

## Build 481 速度原生 helper 试验

在隔离 `native-export-helper` 上对同一 Build 481 速度构建完成三次导出。每次均收到
restore/export/compile 完成事件，产物为 4 秒、120 帧、30 fps、1280×720 H.264/AAC；
`ffmpeg -xerror` 完整解码通过，源草稿与 staging 输入哈希不变。结果位于
`work/build481-ac-20260924/native-trial1/speed-{1,2,3}/result.json`。

为观察慢速的实际源帧映射，又以烧录时间码的 `clip-a.mp4` 构建独立计划：第一段
1.5x（3 秒源片段→2 秒），第二段 0.75x（源起点 1.5 秒→2 秒）。该计划 build 和
verify-build 通过，并完成三次 helper 原生导出；抽帧显示输出 `t=2.5s` 的源时间码为
`00:00:00.400`（理论 0.375 秒在 30 fps 下落到最近帧 0.400 秒），`t=3.5s` 为
`00:00:01.133`（理论 1.125 秒落到最近帧 1.133 秒）。1.5x 段的输出 `t=0.5s` 与
`t=1.5s` 分别显示源 `00:00:00.733` 与 `00:00:02.233`。结果在
`work/build481-ac-20260924/native-trial1/speed-timecode-{1b,2,3}/result.json`，样本图在
`work/build481-resource-audit-20260924/speed-timecode-samples/`。这验证了本机 helper 的
速度渲染和源帧映射。这是最早三档恒速验收；随后新增的三个倍率见[恒速补验](BUILD481-SPEED-20260925.md)。
这些 helper 结果是离线材料映射证据，另有 Build481 UI 保存冷重开验收和正式 Skill 入口检查。

对原 Skill 声明的 0.1–8 倍恒速范围又做了隔离边界调查，记录在
`work/build481-speed-range-20260924/speed-range-evidence.json`。11 个倍率均能构建并通过
`verify-build`；0.1×、0.5×、8× 的单次 helper 导出为 90/90 帧、完整解码且目标 1 秒的
源时间码分别为 0.1、0.5、8 秒。2× 的 3 秒样本却只有 89/90 帧，另一个 2 秒且源入点
0.5 秒的样本为 60/60 帧。新增倍率缺少 GUI 冷重开及正式 Skill 导出，2× 还出现明确的
帧数反例；因此不能把离线构建成功外推为连续 0.1–8 倍原生导出兼容。
后来 0.1×、0.5×、8× 又完成 GUI 冷重开、正式 Skill 导出与画面核对，
才作为三个精确值追加放行；详见[恒速补验](BUILD481-SPEED-20260925.md)。
后续 2× 的目标 2/3 秒与源入点 0/0.5 秒四格复验分别得到 60/60、60/60、
89/90、90/90 帧，只有 3 秒且零入点缺末帧。源素材为精确 30 fps，理论末帧存在，
输出 PTS 无内部断点；现有样本不足以确认根因或安全修复，仍不开放 2×。
矩阵详见 `work/build481-speed-range-20260924/matrix-2x2-20260925/matrix-review.md`。

## Upstream 与本机资源包比对

上游 `mcncarl/jianying-headless` 的 `native_motion.py`、`native_effects.py` 与 fork 中
对应文件一致；速度、六种几何蒙版和叠化的序列化差异不是 Build 481 的阻断点。Build 481
初始阻断来自精确版本 profile 与资源包证据：本机六个蒙版缓存路径的当前文件清单及
tree hash 与上游 11.4.2 捕获完全一致（circle `755f4874…`、rectangle `c8d500f2…`、
line `e548c277…`、mirror `36365677…`、star `ba3fd7eb…`、heart `d72134d8…`），但这些
最初目录的捕获 provenance 只指向 11.4.2；后来 Build481 GUI 已对圆形、线形和镜面
取得资源身份，其中圆形和镜面完成冷重开与正式导出。fork 初始 catalog 的蒙版 `files`
是文件名列表，tree hash 与实际包哈希不同；本轮已按上游固定捕获修复六种文件字典和哈希。
叠化资源 `6724845717472416269/33d3a1ad…` 本机不存在；对本地 effect cache
按资源 ID、包路径和 `config name=dissolve` 检索均无命中。因而不能直接把 11.4.2 捕获
提升为 Build481 捕获。后续已对六种形状逐项补齐 GUI 身份、
保存冷重开、正式构建与导出，因此六项由精确资源门禁开放。叠化与轻微抖动的后续正式验收
另见下节；`native_resources=false` 总门禁保持关闭。

## 六种蒙版 work-only 原生试验

按 `work/build481-ac-20260924/mask_trial.py` 的隔离路径完成剩余五类；六种形状均以
Build481 runtime profile 构建 work-only 草稿，并由本机隔离 helper 导出。各产物为 3 秒、
90 帧、1920×1080、30 fps H.264/AAC，容器 brand 为 `isom`，`ffmpeg -xerror` 全程解码
通过；restore/export/compile 完成事件齐全。抽帧分别显示圆形、矩形、半平面线、镜像、五角星、
心形裁切。源草稿文件清单与复制到 export staging 的媒体/资源逐项哈希保持不变。

每个试验用 work-only catalog monkeypatch 把相应缓存目录的实际文件 dict/tree hash 注入本次
Python 进程，并仅为隔离构建跳过资源 profile 校验。使用的旧缓存 tree hash 是 circle
`755f4874…`、rectangle `c8d500f2…`、line `e548c277…`、mirror `36365677…`、star
`ba3fd7eb…`、heart `d72134d8…`；它们与 11.4.2 捕获一致。该临时覆盖没有改写仓库 catalog、
profile 或生产 gate，也不能证明 Build481 UI 对应相同资源、授予授权或替代 Build481 原生
保存冷重开验收。因此这些 work-only 结果本身只证明当前 helper 能渲染被明确复制的
缓存包；六种形状后续另有正式证据，才能逐项开放生产 gate。

逐项证据位于 `work/build481-ac-20260924/mask-{circle,rectangle,line,mirror,star,heart}-trial/`，
每个目录的 `result.json` 记录 build、资源身份、事件、ffprobe、解码及源/输入哈希；抽帧为
各自 `export/frame-1500ms.png`（圆形为 `export/frame.png`）。线形蒙版的首个计划因带有
无效 `width/height` 被离线校验拒绝；移除这两个字段后，线形构建和导出通过。

## 六种蒙版的正式 Skill 验收

剪映 Build481 GUI 官方逐项选择六种形状后，材料 ID 与缓存路径、全部文件 SHA
分别与六项固定清单一致；六项均保存并冷重开，选中状态和画面裁切保留。
圆形 27 文件 tree SHA=`755f4874…`，镜面 19 文件 `36365677…`，矩形 19 文件
`c8d500f2…`，星形 26 文件 `ba3fd7eb…`，线形 19 文件 `e548c277…`，爱心 26 文件
`d72134d8…`。
正式 Skill 从 GUI 捕获的本机 container 缓存路径读取，各自完成 `build`、`verify-build`；
圆形的正式 build 还完成 `publish`、GUI 保存冷重开和 `verify`，回读报告
`mask/circle` 的 `bytes_verified=true`、四镜像相同、源文件未改。

六项正式 `export` 分别位于
`work/build481-ac-20260924/official-mask-{circle,mirror,rectangle,star,heart,line}-1/`，均返回
`encoded-and-decoded`，3 秒、90/90 帧、1920×1080、H.264/AAC、`ftypisom`，
`ffmpeg -xerror` 全量解码通过，源 build 不变。1.5 秒抽帧分别可见圆形、镜面、矩形、
五角星、爱心和半平面线形裁切。此验收只开放六个固定资源 key；会员/在线素材未下载或使用。
爱心取证时同目录树中另发现 `82432978/d878…` 31 文件包；其 `config.json` 标为 `star`，
与已解密 GUI 爱心材料指向的 `83244815/27ae…` 26 文件路径不同，故不把它计入爱心身份。

## Build 481 叠化与轻微抖动正式验收

逐项 GUI 冷重开、资源 tree/hash、正式 build/verify/publish、剪映保存后结构回读、
helper 和正式 Skill 导出证据见[叠化与特效验收](BUILD481-TRANSITION-EFFECT-20260924.md)。
叠化正式 Skill 输出为 168/168 帧，轻微抖动为 90/90 帧；均为 H.264/AAC、`isom` 且完整解码。
叠化同相测试音约 +6.03 dB，须检查真实音频。轻微抖动正式 Skill 链路回读 effect 轨 1 段、
range 0.15、speed 0.33，27 个源文件和两份 26.6.2 编译缓存字节匹配，四镜像相等、源文件不变。
两项只开放固定资源 key、文件清单/hash 与已声明参数；`native_resources=false` 总门禁保持。
渲染成功不证明账号权益、商用权或再分发许可。原 Skill 不支持曲线变速；STIXGeneral Regular OTF 保存回读失败，
原始 Regular SHA 仍阻断，只有显式生成并验收的别名 SHA 获单项放行，其他字体未验。

## 关键帧与 Monaco 字体原生 helper 试验

以 `all-keyframes-build` 执行三次隔离 helper 导出；每次输出均为 4 秒、120 帧、
1280×720 H.264/AAC，通过完整解码，且源草稿及全部 staging 依赖哈希不变。每次 staging
都包含 SHA256 为 `e110b2fb…85c028` 的 Monaco TTF，和系统 `/System/Library/Fonts/Monaco.ttf`
字节相同。输出抽帧可见字幕；视频画中画随关键帧移动、放大和旋转，音频分析显示 BGM
220 Hz 音量随 `0.5→0.8` 上升、画中画 660 Hz 音量随 `0.7→0.4` 下降。结果在
`work/build481-ac-20260924/native-trial1/all-keyframes-{1,2,3}/result.json`，抽帧在
`work/build481-resource-audit-20260924/keyframe-export-samples/`。这是 helper 的隔离渲染证据，
其隔离工程随后在剪映 GUI 保存并冷重开，通过结构回读；这仍不是正式能力门禁验收。
