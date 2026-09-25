# Build 481 隔离草稿的 GUI 保存与冷重开

**当前暂停：**正式 `gui-cycle` 入口在创建作业前失败关闭。主页搜索命中
目标草稿并不保证随后点击进入的就是该草稿；旧实现未回读编辑器内的
草稿名称和绝对保存路径。以下命令和历史报告仅保留为修复后的验收说明，
在身份检查补齐、重新验收前不能据此放行任何功能。

在已通过 `publish` 登记、且位于核心项目 `work/` 的隔离构建上运行。开始前须让剪映主程序正常退出；工具发现仍有剪映主进程会直接拒绝，避免碰到用户正在编辑的工程。

```bash
export JIANYING_HEADLESS_ROOT=/absolute/path/to/jianying-headless
python3 "$HOME/.codex/skills/yichen-jianying-edit/scripts/headless_draft.py" gui-cycle \
  --build "$JIANYING_HEADLESS_ROOT/work/某次隔离构建/build" \
  --out "$JIANYING_HEADLESS_ROOT/work/新的-gui-验收目录" \
  --rounds 1
```

`--out` 必须是尚不存在的 `work/` 子目录，`--rounds` 为 1–3。入口先校验已固定的核心源码、Swift AX 工具、Build 481 app、原生库和 codec 身份；只允许匹配本机首页草稿的隔离构建。需要 macOS 已向运行工具授予“辅助功能”权限。

每轮通过 Accessibility 唯一定位草稿卡并打开，确认编辑器节点，发送保存，执行 `verify`，从剪映菜单正常退出并确认主进程消失，再冷启动重开、回读和退出。报告在 `result.json`，记录保存前、保存后、冷重开结构与源素材 SHA-256；失败时标记 `failed` 并保留证据，不强退程序或继续导出。

这是草稿 GUI 生命周期验收入口，不是任意时间线编辑入口。`verified` 只说明该隔离草稿打开、保存、冷重开和结构/源哈希检查通过。仍需逐项检查目标功能的 GUI 状态、画面、声音和正式原生导出；不能从该结果开放曲线变速、会员资源或未验证资源。证据与限制见核心项目 [Build 481 GUI 自动化](../../../docs/BUILD481-GUI-AUTOMATION.md)及[完整能力矩阵](../../../docs/BUILD481-FULL-CAPABILITY-MATRIX.md)。
