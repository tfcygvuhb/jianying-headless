# Build 481 隔离工程 GUI 保存与冷重开记录（2026-09-24）

本记录只涵盖隔离测试工程。GUI 操作为剪映专业版 11.4.0 Build 481、Bundle ID
`com.lemon.lvpro`；运行环境身份与应用、动态库和 codec 哈希见
[Build 481 基线](BUILD481-BASELINE-20260924.md)。`publish` 仅把新草稿登记到本机首页，
不是对外发布。所有新草稿位于剪映项目目录中带有本轮专属名称的独立路径。

## 执行方式

每项先用 `verify-build` 核验离线 build，再经 `publish` 登记。剪映关闭后用首页搜索草稿名
打开目标工程，确认标题、保存位置、预览和时间线；发送 `Cmd+S` 保存，再从剪映应用菜单
选择“退出”。随后通过 CUA 冷启动剪映，并从首页重新打开同一草稿。每次退出后用 `ps` 检查主编辑器进程
不存在；退出时 CUA 偶尔返回超时，但进程检查和随后冷启动首页状态均确认应用已退出。

## 基础视频、文字、本地音频

三份工程分别构建、发布，目录与 ID 互异。下列素材哈希取自 build 清单；对应 `publish`
回读的 `source_files_unchanged=true`、`four_mirrors_equal=true`。这证明构建素材未被
publish 修改，不代表记录了原草稿的前态哈希。

| 类别 | 隔离工程 / 草稿 ID | Build SHA-256 | 源素材 SHA-256 | `publish` 回读 | GUI 保存与冷重开 |
| --- | --- | --- | --- | --- | --- |
| 视频 | `B481-Accept-video` / `5D5225E8-73B9-48C6-99EB-ED626EAD9B41` | `9beaf5a652513542606d3c4acd543987a515c039f8e96e0dff2680f2ce5039b6` | `clip-a.mp4` `d2d25a007fa1759cd9c68db419842138904421af229588f172830562e29f7a16` | `created`；1 个 video 段；source unchanged；四镜像一致 | 通过。标题/路径匹配；时间线视频与预览画面正常载入；保存、完全退出、冷启动复开成功 |
| 文字 | `B481-Accept-text` / `E9287C53-AFD3-4D03-9914-51CB7F2C1239` | `6be82461598bdaa12d8a8cdd709e13544e41b30ac067386dca01e496785781a2` | `clip-a.mp4` `d2d25a007fa1759cd9c68db419842138904421af229588f172830562e29f7a16` | `created`；1 个 video + 1 个 text 段；source unchanged；四镜像一致 | 通过。标题/路径匹配；预览与文字轨道“Build 481 Text”存在；保存、完全退出、冷启动复开成功 |
| 本地音频 | `B481-Accept-audio` / `1E921A66-E1AF-4800-A773-730119311D59` | `2775674707c62c1bd86ff476598e5af974ebff69f75d31554713ebd84585ea78` | `clip-a.mp4` `d2d25a007fa1759cd9c68db419842138904421af229588f172830562e29f7a16`；`bgm.wav` `070f47f31d46fd915596ca79ac442d13ece193ccec70d2977202a8f127d46719` | `created`；1 个 video + 1 个 audio 段；source unchanged；四镜像一致 | 通过。标题/路径匹配；时间线上本地 `bgm.wav` 音轨存在；保存、完全退出、冷启动复开成功 |

三份工程各自均在剪映首页可见，并由首页搜索后打开；视频与文字示例画面在预览和时间线
正常呈现。本项只验证打开、保存与冷重开，不执行导出，也不据此宣称最终音画成片验收。

证据位于 `work/build481-ac-20260924/category-fixtures/{video,text,audio}/`：
`build/build.json`、`publish-audit/result.json`、`publish.stdout`、`publish.stderr`；三项
`verify-build` 输出记录于 `work/baseline-20260924/` 外的当轮命令临时结果
`/tmp/b481-verify-{video,text,audio}.json`。没有保存本轮前原有草稿的哈希；本轮没有对
既有项目执行保存或编辑。

## 变速片段（speed fixture）

草稿 `Audit-B481-Speed-5a6aee93d1`，ID
`071068A6-9A30-4F8F-B804-A7D64CC352DD`，build SHA-256
`7c2d9d2c5a1e616766e3cc4be2282d9be963f63449f095b9046defb90eb150df`。素材：
`clip-a.mp4` `d2d25a007fa1759cd9c68db419842138904421af229588f172830562e29f7a16`、
`clip-b.mp4` `600ac0f18d6f391f178722f2cf46715dad93ae61c0e482506881336459d37fba`、
`bgm.wav` `070f47f31d46fd915596ca79ac442d13ece193ccec70d2977202a8f127d46719`。发布回读
为 `created`，source unchanged，四镜像一致。GUI 显示两个变速片段：1.5× 与 0.8×，
各 2 秒，总时长 4 秒。播放计数从起点推进至 `00:00:04:00`，预览有画面；正常保存、退出，
冷启动后再次打开，变速标签与两段时间线仍在。

结论：变速工程能保存并冷重开；播放器能走完整个 4 秒时间线。此处未对导出文件作验证，
也未进行可重复的听感检查，因此不把 UI 播放计数作为变速导出或音频播放通过的证据。

## Monaco 字体、普通字幕、九通道关键帧

草稿 `Audit-B481-AllKeyframes-80a1823504`，ID
`62A81641-4064-4C9E-80F1-DD38C2C44028`，build SHA-256
`de4e03022e50a39f18ccb8caa77673a76cd68ef2be4a80b6693e06bbc7312bce`。素材：
`clip-a.mp4` `d2d25a007fa1759cd9c68db419842138904421af229588f172830562e29f7a16`、
`clip-b.mp4` `600ac0f18d6f391f178722f2cf46715dad93ae61c0e482506881336459d37fba`、
`bgm.wav` `070f47f31d46fd915596ca79ac442d13ece193ccec70d2977202a8f127d46719`。
字体资源是系统 `/System/Library/Fonts/Monaco.ttf`，SHA-256
`e110b2fb6248c654878dee87e9805ac0b2afc8fab19099cf92bfe12ea085c028`。发布回读为
`created`，source unchanged，四镜像一致；`verify-build` 通过。

GUI 首次打开时，标题、保存路径、两条视频轨、字幕“offline keyframe fixture”和音频轨均
可见；字幕呈等宽字形，外观与 Monaco 一致。点击时间线约 1 秒处后，motion 轨的叠加片段
相较起始位置向右移动并变大，符合所构建的 x/y/scale/rotation/opacity 关键帧方向。普通字幕
及关键帧布局能够被剪映载入并显示。

解锁后再次对该隔离工程执行 `Cmd+S`，再经剪映菜单“退出”正常关掉主进程；`pgrep` 确认
主编辑器进程不存在。通过 CUA 冷启动剪映，从首页打开同一草稿，预览、轨道和字幕均重新
载入。随后运行 `headless_draft.py verify --build .../all-keyframes-build` 回读通过：状态
`verified`、时长 4,000,000 us、两条视频轨合计 3 段、文字 1 段、音频 1 段、字体文件 1 个，
四份活动镜像相同、素材源未改、无需原生缓存依赖。冷重开画面仍可见 Monaco 等宽字幕和关键帧
运动状态；音频未进行听感验证。

## Build 481 原生圆形蒙版

独立 build `Audit-B481-Mask-Dissolve-20260924`，草稿 ID
`85B0D0C4-C8D6-4B36-84AF-701697FD569D`，timeline ID
`490AA9B6-5F0C-44A2-BF02-22D38BFDA0A0`，Build SHA-256
`313e7940f8230683c9154a420fc53bd0576137aa710ee9742c5cffe3f96457d1`。本地素材为 clip-a 与
clip-b，SHA-256 分别为 `d2d25a007fa1759cd9c68db419842138904421af229588f172830562e29f7a16` 和
`600ac0f18d6f391f178722f2cf46715dad93ae61c0e482506881336459d37fba`。`publish` 回读为
`created`，source unchanged、四镜像一致；未修改 build 源素材。

在 Build 481 剪映 GUI 中选中 clip-a，进入“画面 → 蒙版”，启用蒙版并点击“圆形”。预览
显示明显圆形裁切。GUI 保存并退出主进程后冷启动剪映，从首页重新打开本工程；再次选中
clip-a 时预览仍呈圆形，蒙版设置中圆形项保持选中。解密保存后的 `draft_info.json`，得到
`common_mask`：resource ID `7356934080102928946`、`resource_type=circle`、名称“圆形”，
材料 ID `17F219E3-834E-473B-B8BB-7B84C4600B91`，constant material ID
`11C918F0-4A37-4B39-806A-1CF7C655D836`，缓存目录
`~/Library/Containers/com.lemon.lvpro/Data/Movies/JianyingPro/User Data/Cache/effect/82432977/3ab1c47350d987c8ad415497e020a38b`。

缓存树有 27 个文件；逐文件 SHA-256 与现有 `mask/circle` catalog 完全一致，缺失、额外或
哈希不匹配项均为 0，tree SHA-256 为
`755f487494e041e0adceaff3c1a747b1238773c071fe3297d1911112cccd3946`。因此 Build 481 UI 所选
圆形蒙版的原生资源身份及缓存内容与 catalog 捕获一致；这项 GUI 重开证据可供版本化 catalog
审查。其他五种本地蒙版的独立 GUI 选择和冷重开结果见下方矩阵。

同一工程的剪映“转场 → 叠化”分类中，AX 树包含名为“叠化”的素材卡；卡片显示蓝色菱形标记
和下载箭头。为避免下载或使用可能的会员资源，没有点击下载或应用，故没有生成 Build 481
叠化材料 ID、实际缓存路径或包哈希，转场 GUI 验收仍未完成。

同一隔离工程另捕获以下形状身份。六种形状均在 Build 481 官方 UI 中逐项选择并保存；圆形、
镜面、矩形、星形、线性、爱心各自均完成正常退出、冷启动复开和预览/所选蒙版复核。GUI
保存后的 `draft_info.json` 通过 Build 481 专用 pinned codec 解密读取，所记录的资源 ID、类型、
材料名与路径来自草稿本身。矩形、线性、圆形、镜面、星形和爱心缓存逐文件哈希与当前 catalog
对应 capture 完全一致。

| UI 形状 | resource ID / type | Build 481 缓存目录 | 文件数 / catalog 比对 | GUI 冷重开 |
| --- | --- | --- | --- | --- |
| 圆形 | `7356934080102928946` / `circle` | `Cache/effect/82432977/3ab1c47350d987c8ad415497e020a38b` | 27/27 相同；tree SHA `755f487494e041e0adceaff3c1a747b1238773c071fe3297d1911112cccd3946` | 通过；见上文 |
| 线性 | `7356933362960831003` / `line` | `Cache/effect/82432976/4c6a0ef5de6a844342d40330e00c59eb` | 19/19 相同；tree SHA `e548c277fb2a6e06739855160a985a676221b19e9c4a65b60c8d75df1aea3c29` | 通过；本轮单独重选、保存、退出并冷重开，线形预览保持 |
| 镜面 | `7356933823327638042` / `mirror` | `Cache/effect/82432979/95ac211c99063c41b86b9b63742f4a6d` | 19/19 相同；tree SHA `36365677e9ef362fdba0a5a9169cd9427c85f3ebecfc16f98c7d17a21bef3977` | 通过；退出后冷启动复开，镜面项与预览仍在 |
| 矩形 | `7356934318301647410` / `rectangle` | `Cache/effect/82432980/02b8999168d121538a98ea59127483ef` | 19/19 相同；tree SHA `c8d500f2840e387e372744f6f44e1d2128e29c94df3dc482cf18a8de7d2f0ec6` | 通过；退出后冷启动复开，矩形预览仍在 |
| 星形 | `7416258989467374091` / `pentagram` | `Cache/effect/83244852/7ff81ba985da9aae07b69c5b77ea7e9a` | 26/26 相同；tree SHA `ba3fd7ebd571eba4f3383343eb7b8f6f504dfef8d6477af3bbe49bd8c67f2a8e` | 通过；退出后冷启动复开，星形预览仍在 |
| 爱心 | `7416258912162157068` / `heart` | `Cache/effect/83244815/27ae3c55bb97e470a75f61a8d34832bf` | 26/26 相同；tree SHA `d72134d8c23f46d9d2ca3b2d7171908285487f2a1cb69cdb57593d427e422936` | 通过；本地卡无会员/下载标记，保存冷重开后爱心预览仍在 |

爱心身份来自 GUI 保存后的 `common_mask`：名称“爱心”、`resource_type=heart`、缓存绝对路径
`~/Library/Containers/com.lemon.lvpro/Data/Movies/JianyingPro/User Data/Cache/effect/83244815/27ae3c55bb97e470a75f61a8d34832bf`。
工作区内另有 31 文件目录 `Cache/effect/82432978/d87811b6bae0c570ed982a8d06eefe91`，其
`config.json` 的 `name=star`，不是本次爱心材料；不用于爱心身份或完整性比对。

本轮线形 GUI 冷重开后运行 `python3 engine/jy14_headless.py verify --build
work/build481-resource-ui-20260924/build`，状态 `verified`、source unchanged、四镜像一致。
该 CLI 回读针对 publish 时无原生蒙版的原始 build provenance，因此报告仍显示 0 个
native resource bindings；线形资源身份和持久化证据来自冷重开后的解密草稿和 GUI 预览，不将
这份 verify 输出误记为原生资源绑定验证。输出保存在
`work/abi-static-verifications-20260924/line-mask-verify.json`。

### “轻微抖动”特效本地可用性

在同一隔离工程打开“特效”库并搜索“轻微抖动”。搜索结果中存在名为“轻微抖动”的卡片，
没有蓝色会员菱形，但卡片右下角显示下载箭头，说明当前不能直接本地选择；没有点击或下载，
也没有把它应用到工程。故 Build 481 的轻微抖动 GUI 资源身份、缓存和冷重开均未验收，
保持门禁关闭。其他搜索结果中部分卡同时带会员菱形与下载箭头。

### 文字 Y/旋转隔离草稿

`work/build481-text-keyframes-20260924/build` 以 `B481-Text-Y-Rotation-Keyframes` 登记到首页；
草稿 ID `DD13C7F7-CA48-4C0F-8E65-7E8D71ED5CB4`，timeline ID
`D317602A-BBCA-484B-AA0A-2AC71BD99992`。离线 build、publish 和 GUI 后 `verify` 均通过，
时长 3 秒，含 1 个视频段和 1 个文字段，源素材 SHA-256 为
`d2d25a007fa1759cd9c68db419842138904421af229588f172830562e29f7a16`；publish 回读
`source_files_unchanged=true`、`four_mirrors_equal=true`。

首次打开时预览显示 `Y POSITION / ROTATION` 文字，文字斜置并处于画面下方；Cmd+S 后经
剪映菜单正常退出，确认主进程退出，再冷启动并从首页复开。复开预览仍显示相同斜置文字和
纵向位置；再次保存后 `verify` 为 `verified`，时长、video/text 轨段数量和镜像一致。GUI
冷重开与结构回读通过；Build 481 的 y/rotation 正式导出验收仍须以 parent 的正式 Skill
导出与媒体核对为准。

## 哈希与范围边界

素材哈希均来自相应 build 清单；各项 `publish-audit/result.json` 的
`source_files_unchanged=true` 与 `four_mirrors_equal=true` 是本轮已有证据。没有在打开 GUI
前对三个原有用户草稿逐文件保存基线，因此不声称已有草稿经过本轮前后哈希对比；本轮未对
原始工程执行保存或编辑。原始输入素材路径与哈希见每项 build 清单。所有回读报告、首页索引
审计与 stdout/stderr 留在本地 `work/` 目录；未纳入仓库源码文件。

后续步骤：叠化卡带蓝色菱形标记和下载箭头，轻微抖动卡有下载箭头；两项均保持未下载、
未应用和未验收。爱心缓存与 catalog
identity 已逐项匹配，但是否打开对应 Build 481 per-key gate 由资源/导出验证决定；其他蒙版的
正式导出状态见能力矩阵，不以 GUI 冷重开单独替代媒体验收。
