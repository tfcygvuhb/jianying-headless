# Build 481 隔离草稿 GUI 生命周期工具

**2026-09-26：正式 `gui-cycle` 已在固定的 Build 481 隔离工程范围内恢复。**
旧实现只核对编辑器时间线节点和目标草稿的磁盘 `verify`，不能证明打开了
指定工程；旧 `verified` 报告仍不能单独作为身份凭据。修复后，主页先筛选
精确草稿名，再要求唯一 `HomePageDraftTitle:<名称>` 的当次 AX 框完整落在
唯一 `HomePageDraft` 卡片框内，才点击该卡。每次打开、保存后、冷重开
都以唯一主进程 PID 绑定前台窗口截图：Vision 必须在“草稿名称”右侧
读到精确名称；同一 PID 的 `lsof` 在截图前后必须只持有目标绝对目录
的唯一 `.locked` 和资源文件句柄。保存动作前 Swift 层再次读取相同
句柄并拒绝任何其他草稿路径；Cmd+S 定向发送给已核对的剪映 PID，发送后
再次检查目标句柄。这里的绝对路径来自活动进程文件句柄，
不依赖容易将小写 `l` 误读为大写 `I` 的完整路径 OCR。

最终版本经**已安装 Skill 入口**对 1×、2× 两个不同草稿各跑三轮，
每轮打开、保存后、冷重开身份门均通过，结构四镜像一致、源素材 SHA 未变，
剪映正常退出；证据分别在
`work/build481-identity-final-1x-3rounds-20260926/result.json` 和
`work/build481-identity-final-2x-3rounds-20260926/result.json`。
随后增加保存命令内的目标句柄复核，故意给 1× 活动编辑器传入 2× 目标
时在发送 Cmd+S 前拒绝，见
`work/build481-identity-save-negative-20260926/wrong-save.json`；
该最终保存门对两份草稿各再通过一轮正式 Skill 回归，见
`work/build481-identity-saveguard-{1x,2x}-20260926/result.json`。
按 PID 定向发送 Cmd+S 与保存后句柄复核后，两份草稿又各通过一轮，见
`work/build481-identity-pid-directed-20260926/result.json` 与
`work/build481-identity-pid-directed-2x-20260926/result.json`。
这只证明已登记、含本机资源文件、当前唯一剪映窗口的隔离工程生命周期，
不会放行 2× 正式导出或任何未验效果。若无法取得唯一锁/资源句柄、窗口、
草稿名或原生身份，入口仍失败关闭。

上述 GUI 冷重开后的 1× 工程又经已安装 Skill 正式原生导出：
`work/build481-identity-postgui-export-1x-20260926/render.mp4` 为标准
`isom` H.264/AAC、90/90 帧，完整解码且逐帧时码 0–89 一致；对应逐帧记录在
`fullframe-audit.json`。这是一份 1× 复核证据，不扩展非 1× 倍速门禁。
AX 框与鼠标事件之间、同一剪映进程内切换工程时仍有很短的状态竞争窗口；
因此工具只操作登记过的隔离草稿，失败时保留现场和记录，不能将它用于
用户当前正在编辑的工程。
截图证据工具在创建输出目录前检查父目录解析后的真实路径；符号链接越界
负例被拒绝且未在 `work/` 外创建目录。

历史调查保留：仅点精确标题节点的单击/双击不能进入编辑器；首页的
`AXDocument` 无值、`AXURL` 缺失。独立 1× 截图中，完整路径 OCR 的
小写 `l`/大写 `I` 混淆可在 1.0 置信度发生，因此不用它作为路径门。
原始记录在 `work/build481-identity-live-probe-20260925/LIVE-RESULT.md`、
`work/build481-gui-identity-20260925/REPORT.md` 和
`work/build481-identity-generic-click-20260925/LIVE-RESULT.md`。

`tools/gui_cycle.py` 只用于已由本项目构建并登记的 `work/` 隔离草稿。

`jy14-edit-build/v1` 的记录、源工程/媒体 SHA 与专用 live verifier 已接入同一
验收流程；当前 `existing_edit_publish=false`，编辑副本在 GUI 启动前拒绝。
该分支只有离线契约测试和门禁负例，不能当作编辑副本保存冷重开证据。
新建工程的命令为：

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
启动每轮 GUI 前读取 macOS 会话锁屏状态；`CGSSessionScreenIsLocked=1` 时
直接报错，不在无窗口的锁屏会话中等待或点击。这个检查来自 1× 带时码
隔离草稿一次失败的冷重开尝试，记录在
`work/build481-speed-one-gui-cycle-20260925/result.json`；该次没有 GUI
通过证据。
在解锁的本机，系统会省略该锁屏字段，故预检同时要求控制台会话已登录，
只有明确报告锁定才拒绝。修正后同一 1× 草稿通过正式已安装 Skill 的
`gui-cycle` 一轮，详见
`work/build481-speed-one-gui-unlocked-20260925/result.json`。

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

字体负例另有 work-only 容错生命周期原型和 Vision 字形比较器，记录在
`work/build481-font-qualification-next-20260925/REPORT.md`。三次 STIX Regular
原生诊断导出完整解码，抽帧像素相同；STIX 与 Arial 控制的归一化字形掩膜
Dice 约 0.227，说明该短句可区分两种字体。该轮因会话锁屏未完成 GUI。
解锁后的新隔离工程已运行三轮保存、正常退出和冷重开；12pt `STIX 123`
样本的原始冷重开 JSON 差异为 29/0/1 项，逐项核对资源占位符、默认字段和
平台元数据后，三轮实质差异均为 0，字体 SHA 与四镜像、源素材哈希不变。
三张 GUI 预览的字形掩膜一致，但与原生 STIX、Arial 导出帧的比较缺少已知
正确 GUI 正控制，视觉身份仍为 `INCONCLUSIVE`。历史 42pt 原始 STIX Regular
回退负例也未被推翻，因此该 SHA 仍失败关闭。详情见
`work/build481-font-qualification-next2-20260925/REPORT.md`。
