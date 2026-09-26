# Build 481 静态 OTF/TTF 隔离导出记录

日期：2026-09-24

环境：macOS Apple Silicon，剪映 11.4.0 Build 481

## 验证范围

从本机 `/System/Library/Fonts/Supplemental/` 选择一个静态 OTF 和一个非 Monaco 静态 TTF。分别使用正式 `build`、`verify-build` 入口构建新隔离草稿，再用现有 Build 481 `native-export-helper` 对 staged timeline 直接导出一次。未调用剪映 GUI；本报告不等同于 GUI publish、保存或冷重开验收，也不自行开放生产字体门禁。

## 字体和构建

| 类型 | 字体路径 | SHA-256 | 字体信息 | 构建路径 |
| --- | --- | --- | --- | --- |
| 静态 OTF | `/System/Library/Fonts/Supplemental/STIXGeneral.otf` | `5add3f3f2bd7fd897d2fa5ccbe468607c52111dc44cdfaaf2d851a574f5357a7` | STIXGeneral Regular，3302 glyphs | `work/build481-font-coverage-20260924/stix-general-build` |
| 静态 TTF（非 Monaco） | `/System/Library/Fonts/Supplemental/Arial.ttf` | `525979822591a3447cfc49d943d6f7683508e25543407871c0ed8fed05fd2bd9` | Arial Regular，3381 glyphs | `work/build481-font-coverage-20260924/arial-ttf-build` |

两种字体均通过仓库的静态 sfnt 字体解析校验；额外用 `fontTools` 检查，均无 `fvar`、`gvar`、`CFF2` 可变字体表，测试文本所需字符均在 Unicode cmap 中。

两次 `build` 都返回 `built`，`font_files=1`、`live_written=false`、未使用 UI 准备及原生资源；对应 `verify-build` 都返回 `verified` 且 `live_written=false`。计划与结构化输出在 `work/build481-font-coverage-20260924/plans/`、`*-build.json` 和 `*-verify.json`。

## 隔离原生导出

两次均使用 `work/build481-ac-20260924/native-trial1/native-export-helper`（SHA-256 `dfefd8517968a5c801eadfd385060c455b0d07950ea8d446bc9a862641a57d03`）执行独立 sandbox 导出。每次 helper 返回码为 0，包含 restore 与完成事件；`ffprobe` 检查为 1280×720、30 fps、90 帧、约 3 秒 H.264，AAC 音轨存在，major brand 为 `isom`；容器头 `ftyp` 独立检查为 `isom`；两次 `ffmpeg -xerror` 全量解码返回码均为 0。

| 字体 | 导出文件 SHA-256 | 可见字形抽帧 |
| --- | --- | --- |
| STIXGeneral OTF | `625d467a2a3a65ab459944e3fa6a97ec8df347fd09db8dc9801669f79ac1761e` | `work/build481-font-coverage-20260924/exports/stix-general/visible-glyphs.png` |
| Arial TTF | `f75b4acc2cbe63ef1baedbb15e2712288b3e9f7b99023cfa7c935e56d93905c6` | `work/build481-font-coverage-20260924/exports/arial-ttf/visible-glyphs.png` |

抽帧中分别可读出 `STIX GENERAL 123` 和 `ARIAL TTF 123`，字形外观与两种字体不同，证明导出画面使用了对应字形。

字体原文件与测试背景视频在导出前后哈希相同。哈希清单和完整 ffprobe/解码数据见 `work/build481-font-coverage-20260924/source-and-font-sha256.txt`、`source-and-font-sha256-after.txt` 与 `export-summary.json`。

## 结论与限制

本轮证明本机这两个特定静态字体可通过隔离构建及 helper 原生渲染，且输出字形可见、媒体可完整解码。它没有证明剪映 GUI 打开、保存和冷重开流程；也没有证明任意 OTF/TTF 或其他字体适配。生产门禁仍应按精确字体哈希和后续 GUI 验收结果处理。
