# Build 481 文字 Y 与旋转关键帧隔离导出记录

日期：2026-09-24
目标环境：macOS Apple Silicon，剪映 11.4.0 Build 481

## 范围

本次只验证一个隔离草稿中的默认字体文字图层，对 `y` 与 `rotation` 两个通道各使用两个线性关键帧，并通过既有 `native-export-helper` 执行三次隔离原生导出。该记录不代表其他关键帧通道、曲线插值、剪映 GUI 保存/冷重开或生产出口门禁已通过。

## 样本与构建

样本计划位于 `work/build481-text-keyframes-20260924/plan.json`，背景为本机测试视频 `clip-a.mp4`（静音，3 秒）。文字为 `Y POSITION / ROTATION`，未指定字体文件，使用默认字体；画布为 1280×720、30 fps。`y` 在 0 秒和 3 秒分别为 -0.55、+0.55；旋转分别为 -24°、+24°，均为线性端点。

`plan-build` 返回 `built`，`verify-build` 返回 `verified`。构建均报告 `live_written=false`，未用 UI 准备，未引用原生资源；字体文件计数为 0。构建目录 SHA-256：`55ebf623d302fda757e97b0629be28517a859fc3513df881de314e9cebfceb06`。

源素材 SHA-256 前后均为 `d2d25a007fa1759cd9c68db419842138904421af229588f172830562e29f7a16`，未发生变化。

## 原生导出结果

调用 `work/build481-ac-20260924/native-trial1/native-export-helper` 的隔离副本完成 3 次独立运行。三次 helper 返回码均为 0，均观察到 restore 与完成事件。输出均为 1280×720、30 fps、90 帧、时长约 3 秒、H.264/AAC；容器 `major_brand=isom`。每个文件均通过 `ffmpeg -xerror` 全量解码。

| 样本 | 导出 SHA-256 | 字节数 | 结果 |
| --- | --- | ---: | --- |
| 1 | `4c4f92232c76febc2d9821209142207cbc6d65e9cc0c8d4d3ad95105761df554` | 1,567,084 | 完成事件、媒体属性与全量解码通过 |
| 2 | `89436a802bd9b67d09b63794437447b88e73237c901d1d8625f6ed5e50259007` | 1,567,084 | 完成事件、媒体属性与全量解码通过 |
| 3 | `fb52148b3f13751f792e586ddad0a34529a8c9399317c08f128a281488ecdb38` | 1,567,084 | 完成事件、媒体属性与全量解码通过 |

首个样本在 6、45、84 帧抽取的画面见 `work/build481-text-keyframes-20260924/frames-contact.png`：帧 6 的文字位于画面左下且逆时针倾斜，帧 45 移到画面中央并近水平，帧 84 到达右上且顺时针倾斜。位置和旋转变化都在相邻采样时点可辨认，与计划中的 Y 与 rotation 线性端点一致。

## 结论与边界

该特定样本的离线构建、构建验证及 helper 直连原生导出重复性通过，覆盖文字 `y` 与 `rotation` 两个线性通道。它补充了此前仅含文字 `x`/`scale` 的样本缺口。

最初三次 helper 试验没有启动剪映 GUI；当时生产 `native_export.py` 的 Build 481
公共范围仍拒绝 `common_keyframes`。这些试验本身只是隔离 helper 证据，不能单独视为
Skill 正式出口通过。后续证据见下节及 GUI 报告。曲线变速和非线性插值仍未验证。

## 后续正式 Skill 出口复核

在按精确 Build 481 档案、通道和节点形状收窄出口范围后，已安装 Skill 对同一冻结 build
执行一次正式 `export`。结果为 `encoded-and-decoded`，标准 `isom` MP4、1280×720、
30 fps、90/90 帧 H.264/AAC、完整解码通过，源 build 未变化。输出位于
`work/build481-text-keyframes-20260924/official-export-1/render.mp4`；2.8 秒抽帧中，
文字位于右上并顺时针倾斜，符合隔离 helper 的画面。剪映 GUI 已经对该独立草稿完成
首次打开和保存，冷重开与结构回读另记在 GUI 报告；本段正式导出不替代该持久化检查。

## 可复核产物

- 计划与构建：`work/build481-text-keyframes-20260924/plan.json`、`build/`、`build.stdout.json`、`verify-build.stdout.json`
- 三次导出元数据：`work/build481-text-keyframes-20260924/export-summary.json`
- 执行脚本：`work/build481-text-keyframes-20260924/run_trials.py`
- 可视化抽帧：`work/build481-text-keyframes-20260924/frames-contact.png`
