# Build 481 隔离草稿的 GUI 保存与冷重开

**Build 481 隔离工程可用：**正式 `gui-cycle` 现要求主页目标标题与
被点击的卡片具有同一当次 AX 框归属；每次打开、保存后和冷重开均核对
界面 OCR 的草稿名、唯一剪映 PID 持有的目标工程 `.locked` 与资源文件句柄。
保存命令再次检查目标句柄，错填工程在 Cmd+S 前拒绝。1×、2× 两个
隔离工程各通过三轮，保存门另对两者各通过一轮；旧版缺身份回读的
`verified` 报告不能单独作为凭据。此入口不使 2× 导出或高级效果开放。

在已通过新建草稿 `publish` 登记、且位于核心项目 `work/` 的 `jy14-headless-build/v1`
隔离构建上运行。工具有 `jy14-edit-build/v1` 的严格记录校验分支，但 Build 481
的 `existing_edit_publish=false` 会在启动 GUI 前拒绝编辑副本，尚无该类验收通过证据。开始前须让剪映
主程序正常退出；工具发现仍有剪映主进程会直接拒绝，避免碰到用户正在编辑的工程。

```bash
export JIANYING_HEADLESS_ROOT=/absolute/path/to/jianying-headless
python3 "$HOME/.codex/skills/yichen-jianying-edit/scripts/headless_draft.py" gui-cycle \
  --build "$JIANYING_HEADLESS_ROOT/work/某次隔离构建/build" \
  --out "$JIANYING_HEADLESS_ROOT/work/新的-gui-验收目录" \
  --rounds 1
```

`--out` 必须是尚不存在的 `work/` 子目录，`--rounds` 为 1–3。入口先校验已固定的核心源码、Swift AX 工具、Build 481 app、原生库和 codec 身份；只允许匹配本机首页草稿的隔离构建。需要 macOS 已向运行工具授予“辅助功能”权限。

每轮通过 Accessibility 唯一定位与目标标题关联的草稿卡并打开，在保存前、保存后和冷重开时检查同一活动工程的窗口名称与绝对文件句柄，再执行 `verify`。从剪映菜单正常退出并确认主进程消失。报告在 `result.json`，记录截图/OCR、保存前后的 PID 句柄、结构与源素材 SHA-256；失败时标记 `failed` 并保留证据，不强退程序或继续导出。只支持打开时确实持有目标资源文件的隔离工程，其他情况明确失败。

这是草稿 GUI 生命周期验收入口，不是任意时间线编辑入口。`verified` 只说明该隔离草稿打开、保存、冷重开和结构/源哈希检查通过。仍需逐项检查目标功能的 GUI 状态、画面、声音和正式原生导出；不能从该结果开放曲线变速、会员资源或未验证资源。证据与限制见核心项目 [Build 481 GUI 自动化](../../../docs/BUILD481-GUI-AUTOMATION.md)及[完整能力矩阵](../../../docs/BUILD481-FULL-CAPABILITY-MATRIX.md)。
