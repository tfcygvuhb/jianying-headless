# Build 481 隔离草稿 GUI 生命周期工具

`tools/gui_cycle.py` 只用于已由本项目构建并登记的 `work/` 隔离草稿：

```bash
python3 tools/gui_cycle.py \
  --build "$PWD/work/某次隔离构建/build" \
  --out "$PWD/work/新的-gui-验收目录" \
  --rounds 1
```

该命令要求剪映主程序在开始前未运行，核对 Build 481 app/lib/codec 指纹、
build 名称与本机首页草稿路径后才启动 GUI。Swift AX 层按 Bundle ID 选唯一
regular 主进程，以 role、description、title 或 identifier 唯一定位控件；
AX 树若超出完整遍历上限即拒绝，点击后的目标状态必须从原先不存在变成唯一存在。
需要点击但无 AXPress 的草稿卡使用**当次 AX 框**，不保存屏幕坐标。
每次点击后等待编辑器语义节点出现。保存前后和冷重开后分别执行结构 `verify`，
正常从应用菜单退出并确认主进程消失；操作前还先做一次 live `verify`，
每轮记录素材 SHA、草稿文件清单 SHA 与草稿文件变化。
失败保留 `result.json` 和当时 GUI 状态，不强制结束程序，也不交付“通过”结论。

2026-09-25 的 work-only 原型对同一 9 秒、3 段隔离工程完成三轮保存、正常退出、
冷启动重开和 `verify`；三轮均四镜像一致、源素材 SHA 未变，见
`work/build481-gui-ax-20260925/prototype/REPORT.md`。整理后的正式工具又对同一
工程独立跑通一轮，结果在
`work/build481-gui-cycle-formal-20260925-retry3/result.json`。
第一、二次整理版试验因命令行进程的 `NSRunningApplication.isActive` /
`NSWorkspace.frontmostApplication` 状态滞后，在点击前失败；改为读取实时
`AXFrontmost` 后才成功。这两次没有点击或保存目标草稿，失败记录留在独立
`work/` 作业目录。

经代码审查补上“AX 树截断即失败”“点击后状态由不存在变为唯一存在”及 GUI 前
`verify` 后，又通过**已安装 Skill 的正式 `gui-cycle` 入口**独立跑通一轮：
`work/build481-gui-cycle-installed-skill-20260925/result.json` 为 `verified`，
预检、保存后、冷重开三阶段均 `verified`；9 秒、1 轨 3 段、四镜像相同，
源素材 SHA 前后相同，剪映主进程最终不存在。报告记录草稿前后文件清单 SHA。

本工具证明隔离草稿的**生命周期**可由 agent 控制；它不自动选择任意时间线
片段或曲线变速预设。三段相同素材在 AX 树中只有相同描述且没有独立 action/ID，
曲线预设可由 Vision OCR 识别，但 AX 没有可回读的预设选择状态；因此这些编辑
动作仍保持失败关闭。此工具不处理云工程、会员资源获取或用户当前正在编辑的工程。

另在单片段独立草稿 `Build481-Curve-GUI-Sample-20260925` 做了曲线最小实验。
Vision 到 AX 坐标映射经同屏“曲线变速”标签校准误差 <1 pt；对“蒙太奇”文字
中心和上方图卡中心的两次动态点击都未改变“无”的选中边框。保存、冷重开后的
解密草稿只有默认 1× 材料，没有非空曲线；素材哈希不变，最后正常退出。
详见 `work/build481-curve-gui-20260925/REPORT.md`。没有可供序列化/导出
验收的官方曲线样本，曲线能力继续关闭。
