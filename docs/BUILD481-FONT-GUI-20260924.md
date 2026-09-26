# Build 481 本地字体 GUI 验收

本记录覆盖隔离草稿 `Build481-STIXGeneral-OTF`、`Build481-Arial-TTF`、`Build481-OTF-Persist-STIXItalic-20260924` 和 `Build481-OTF-Diagnostic-STIXRegularAlias-20260924`。四份 build 均由 `publish` 创建并登记到剪映首页；源素材来自仓库隔离测试素材，原工程未打开或修改。字体源 SHA、build 与 publish 审计材料保存在 `work/build481-font-coverage-20260924/`、`work/build481-font-gui-20260924/` 和 `work/build481-font-persistence-20260924/`。

## STIX General OTF

- build：`work/build481-font-coverage-20260924/stix-general-build`
- 草稿：`Build481-STIXGeneral-OTF`，ID `C7A747CC-F555-4F2E-A927-74B2097AA27B`
- 字体：系统 Supplemental 目录中的 `STIXGeneral.otf`，SHA-256 `5add3f3f2bd7fd897d2fa5ccbe468607c52111dc44cdfaaf2d851a574f5357a7`
- publish：成功；审计结果为 `created`，1 个视频段、1 个文字段、1 个字体文件，源素材未变、四份草稿镜像一致。
- GUI：预览显示 `STIX GENERAL 123`，字形外观为衬线体。保存前字体面板显示“系统”；没有在字体选择器中下载或应用其他字体。
- 持久化：Cmd+S 后正常 Cmd+Q；检查时剪映主进程已退出（系统 tray helper 尚在）。重新启动剪映并从首页打开同一隔离草稿后，文字仍可见，故文字与画面通过 GUI 冷重开检查。
- 字体绑定：冷重开后用 Build 481 pinned codec 解密草稿。`materials.texts[0].font_path` 与 `content.styles[0].font.path` 都是 `/Applications/VideoFusion-macOS.app/Contents/Resources/Font/SystemFont/zh-hans.ttf`，而 build 预期路径为 `Resources/headless-fonts/5add3f3f2bd7fd897d2fa5ccbe468607c52111dc44cdfaaf2d851a574f5357a7.otf`。草稿内的 OTF 文件仍存在，文件 SHA 与源字体相同；剪映保存时将两处绑定改写为系统字体路径。
- `python3 engine/jy14_headless.py verify --build work/build481-font-coverage-20260924/stix-general-build` 退出码为 1，失败于 `ValueError: Planned font binding changed`。解密草稿和字段对照分别保存在 `work/build481-font-gui-20260924/stix-live-draft_info.json` 与 `stix-font-binding-diff.json`；可复核的 stderr 在 `stix-verify.stderr.log`。
- 结论：STIX OTF 的字体文件可随草稿发布，但 Build 481 GUI 保存没有保留计划字体绑定；该字体的原生保存门禁不通过，不能据此放行 OTF。

## 已放行 Monaco TTF 对照

只读复核此前完成 GUI 保存和冷重开的 `Audit-B481-AllKeyframes-80a1823504`，草稿 ID
`62A81641-4064-4C9E-80F1-DD38C2C44028`。已保存 timeline 的
`materials.texts[0].font_path` 与 `content.styles[0].font.path` 都使用
`##_draftpath_placeholder_0E685133-18CE-45ED-8CB8-2904A212EC80_##/Resources/headless-fonts/e110b2fb6248c654878dee87e9805ac0b2afc8fab19099cf92bfe12ea085c028.ttf`，解算后均精确指向草稿内对应资源；草稿文件仍存在且 SHA-256 为 `e110b2fb6248c654878dee87e9805ac0b2afc8fab19099cf92bfe12ea085c028`。`all-keyframes-live-verify.json` 状态为 `verified`，`font_files=1`、`four_mirrors_equal=true`、`source_files_unchanged=true`。字段与 hash 对照在 `work/build481-font-gui-20260924/monaco-binding-diff.json`。

这与 STIX OTF 的结果不同：Monaco 保存后保持草稿相对路径，STIX 保存后两处路径均被改为系统字体。当前 Monaco 固定 SHA 的证据不能外推到其他静态 OTF/TTF。

## Arial TTF

build：`work/build481-font-coverage-20260924/arial-ttf-build`；草稿 `Build481-Arial-TTF`，ID `244E9FB7-851B-425F-AECB-A695E5928374`，build SHA-256 `6af5d9a9250fa99b1d713b474bac1651176eb54a00ef0c2958568bce03d326f8`。源字体为系统 Supplemental 目录中的 `Arial.ttf`，SHA-256 `525979822591a3447cfc49d943d6f7683508e25543407871c0ed8fed05fd2bd9`。

publish 成功；审计结果为 `created`，1 个视频段、1 个文字段、1 个字体文件，源素材未变、四份草稿镜像一致。首次打开和冷重开后均能看到 `ARIAL TTF 123`，外观为无衬线体；文字属性面板显示“系统”，因此单凭面板标签不把字体名称视作 UI 已确认。没有在字体选择器中下载或应用其他字体。

Cmd+S 后使用 Cmd+Q 正常退出；退出后剪映主进程不存在，仅 tray helper 仍在。冷启动剪映并从首页重新打开同一隔离草稿，文字再次显示。解密保存后的 `draft_info.json`，`materials.texts[0].font_path` 和 `content.styles[0].font.path` 都保持 `##_draftpath_placeholder_0E685133-18CE-45ED-8CB8-2904A212EC80_##/Resources/headless-fonts/525979822591a3447cfc49d943d6f7683508e25543407871c0ed8fed05fd2bd9.ttf`；解算后两者均精确指向草稿中的预期相对路径。草稿内字体文件存在且 SHA 与源一致。保存后 `verify` 状态为 `verified`，`font_files=1`、`four_mirrors_equal=true`、`source_files_unchanged=true`、`native_cache_dependency=false`。

绑定字段和验证回读保存在 `work/build481-font-gui-20260924/arial-binding-diff.json` 与 `arial-verify.json`。固定 SHA 字体另经已安装 Skill 的正式 `export` 路径导出：`work/build481-font-coverage-20260924/official-arial-ttf-1/result.json` 状态为 `encoded-and-decoded`，Build 未变，原生返回码为 0 且完成事件齐全；视频为 H.264、AAC、1280×720、30 fps、90/90 帧，容器 `ftypisom`，`ffmpeg -xerror` 完整解码通过。输出 SHA-256 为 `0c2f309b33916f6712edac8f6dca00f6f7d38fa22dd33bbc78cfe4795daa0068`，1.5 秒抽帧 `frame-1.5.png` 可见 `ARIAL TTF 123`。因此固定 Arial SHA 完成 GUI 持久化、结构回读和正式原生导出验收；面板标签显示“系统”仍是未能通过 UI 直接识别字体名称的限制，不外推到任意字体。

## STIX General Italic OTF 精确 SHA 验收

为判定 Build 481 是否普遍不保留静态 CFF OTF，另用同一 STIX General 字体家族中的 Italic face 构建独立草稿。所有新代码快照、build、审计、回读和 helper 输出均在 `work/build481-font-persistence-20260924/`；原始用户工程未打开或修改。

- build：`work/build481-font-persistence-20260924/project/work/build481-font-persistence-20260924/stix-italic-build`；计划 `.../plans/stix-italic.json`；草稿 `Build481-OTF-Persist-STIXItalic-20260924`，ID `D36A457A-57FE-420E-B495-282CDECA4733`。
- 字体：`/System/Library/Fonts/Supplemental/STIXGeneralItalic.otf`，SHA-256 `7f6bf9cab728febe4ce111bbfbcd16253806dcab0bbe1940ede2782cfc319a72`；build 中 OTF 字节与源哈希一致。
- build、`verify-build`、`publish` 均成功。剪映 GUI 打开隔离草稿，画面显示 `STIX ITALIC 123` 斜体衬线字形；Cmd+S 后正常 Cmd+Q，剪映主进程退出。冷启动并从首页重新打开后，画面仍显示该字形。冷重开后的 `materials.texts[0].font_path` 和 `content.styles[0].font.path` 均保留指向该 OTF 的草稿相对路径，`font.id` 为空；正式 `verify` 返回 `verified`。绑定回读见 `work/build481-font-persistence-20260924/stix-italic-live-binding.json`，冷重开 timeline 解密快照见 `stix-italic-live-after-cold.json`，verify 输出见 `project/work/build481-font-persistence-20260924/stix-italic-verify-live.json`。
- 导出：本轮使用 work-only 隔离副本中的 Build 481 原生 helper 直接执行导出。仅为这次实验在副本 `project/engine/native_export.py` 的 SHA allowlist 加入上述精确测试字体 SHA；原仓库 engine、Skill wrapper pin 和主资源矩阵未改。结果 `project/work/build481-font-persistence-20260924/stix-italic-export-work-only-direct/result.json` 为 `encoded-and-decoded`，native return code 0，导出和恢复完成事件齐全，helper SHA-256 `25575e51bcd0911ac67a6d94513c9a6e57e505ab015832217f26f611194b5914`。视频为 H.264、AAC、1280×720、30 fps、90/90 帧、`isom`；输出 SHA-256 `f8cb62003801e7c4b459690bc6b4c63ff03a8c4e07bf5860ea9003b1ea6bb345`，`ffmpeg -xerror` 全量解码通过。抽帧 `.../stix-italic-export-work-only-direct/frame-1.5.png` 可见 `STIX ITALIC 123`。
- 随后主仓库为上述精确 SHA 加入 Build 481 字体导出门禁，并更新已安装 Skill 的源码 pin。正式 Skill 入口导出 `work/build481-font-persistence-20260924/official-stix-italic-1/result.json` 返回 `encoded-and-decoded`、native return code 0、完成事件齐全、`isom`、H.264/AAC、1280×720、30 fps、90/90 帧、全量解码通过且源 build 未变。输出 SHA-256 `ef128c904469de5dbd115ad4baee160e0d26c36a1478a1c1f6097a6c72fafe2c`；`frame-1.5.png` 已人工查看，显示斜体衬线 `STIX ITALIC 123`。
- 该测试计划将底图视频音量设为 0。输出含 AAC 音轨且可完整解码，但 `volumedetect` 的平均及峰值均为 -91 dB；因此本次验收不能证明声音听感或音频质量。

## Regular 与 Italic 对照结论

静态对照保存在 `work/build481-font-persistence-20260924/static-font-comparison.json`。STIXGeneral Regular 与 Italic 都是同一目录、相同 sfnt 表集合、CFF 1.0、OS/2 weight 400、vendor `STIX`、family `STIXGeneral` 的静态 OTF。Regular face 的 `fsSelection=64`、`head.macStyle=0`、subfamily/PostScript name 为 `Regular`/`STIXGeneral-Regular`，有 3302 glyphs；Italic face 为 `fsSelection=1`、`head.macStyle=2`、`Italic`/`STIXGeneral-Italic`，有 1063 glyphs。

两份 GUI 保存结果不同：Regular 保存后两处字体绑定被 Build 481 改写为应用的 `SystemFont/zh-hans.ttf`，而 Italic 保存和冷重开后仍引用草稿 OTF，且 helper 能按该精确 SHA 渲染。现有对照证明该问题不等同于“剪映不支持任何静态 CFF OTF”，但无法仅凭这两个 face 判定是哪个名称或 face flag 触发 Regular 回退。原 STIXGeneral Regular SHA 仍不通过 GUI 保存门禁；Italic 结果只支持它自己的精确 SHA，不外推到任意 OTF。Regular 保存前后的 material 差异在 `work/build481-font-persistence-20260924/stix-regular-serialized-node-diff.json`。

## STIXGeneral Regular 的显式本地别名路径

针对上述原始 SHA，`tools/make_stix_regular_alias.py` 提供可选的本地转换。它只接受
`/System/Library/Fonts/Supplemental/STIXGeneral.otf` 和原始 SHA
`5add3f3f2bd7fd897d2fa5ccbe468607c52111dc44cdfaaf2d851a574f5357a7`，
要求 `fontTools==4.60.2`，在新的 `work/` 路径生成别名字体，拒绝覆盖既有文件，
不修改系统或用户源字体。调用示例：

```bash
python3 tools/make_stix_regular_alias.py --output "$PWD/work/stix-regular-alias.otf"
```

生成 SHA 固定为 `154e149bfdd2daf1f9560b8103bc3484c327a4969710339ea9e8b5a1247a0717`。
脚本仅改 sfnt name 表中的 family/unique/full/PostScript 名称、对应 CFF 名称和固定
`head.modified` 元数据；字形程序、度量、cmap、weight、Regular face flags 保持不变。
两次独立生成与 GUI 验收 fixture 逐字节一致，见
`work/build481-font-persistence-20260924/project/work/build481-font-alias-diagnostic-20260924/generator-determinism-report.json`。
使用时在新建计划的文字 `font_path` 中显式填写输出别名字体的绝对路径。

别名隔离草稿 `Build481-OTF-Diagnostic-STIXRegularAlias-20260924` 完成 `build`、
`verify-build`、`publish`、剪映保存、完全退出和冷重开；两处字体绑定均指向草稿内
别名 OTF，正式 `verify` 为 `verified`，四镜像相同且源文件未变。work-only helper
导出为 90/90 帧、`isom`、H.264/AAC、全量解码通过。随后固定别名 SHA 加入
Build 481 精确导出门禁，已安装 Skill 正式出口的
`work/build481-font-persistence-20260924/official-stix-regular-alias-1/result.json`
同样返回 `encoded-and-decoded`、90/90 帧、全量解码且源 build 未变；输出 SHA
`4cf957bb4e4e4cf7e9967eea002baa9373380bb2b25a9e4dabd73b12c299b936`，
1.5 秒抽帧显示 Regular 衬线字形。测试底片静音，音轨存在不能证明听感。
原始 Regular OTF 仍会在剪映保存时回退，继续被正式门禁拒绝；此方法仅适用于
上述精确源字体，不推广到任意 OTF 或自动改写用户提交的字体。
