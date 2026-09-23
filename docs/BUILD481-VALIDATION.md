# 剪映 11.4.0 Build 481 分阶段验收

本页只适用于精确运行档案 `jy14-headless-macos-11.4.0-build481`。它记录证据，
不因为某项离线测试通过而自动开启能力。应用签名、Team ID、动态库和 codec 哈希仍由
`doctor` 每次重新核对。

## 当前结论

| 分类 | 结果 |
| --- | --- |
| 已验证 | 精确应用身份；profile 专用 codec；基础视频、文字、音频的离线构建；`publish`（首页登记+热注册+冷重开）；`existing_edit`（文字替换/音量编辑副本 publish）；`verify-build`/`verify` 回读；所有禁用能力的 fail-closed 门禁 |
| 部分验证 | 普通字幕的离线构建；编辑副本的冷重开 UI 验证（首轮通过） |
| 未验证 | Build 481 的本地字体、关键帧、贴纸、调整图层；三次独立原生导出验收；原生导出 ABI 与成片；原生资源矩阵中的特效/转场/滤镜/蒙版/复合片段 |
| 明确阻断 | `native_export` 缺 Build 481 ABI 偏移量证据；`native_resources` 各分项缺独立验收；复合片段保存持久化问题 |

## 阶段 1：publish

状态：`enabled`，`publish=true`（2026-09-23）。

`com.apple.provenance` 和 `com.apple.macl` 已知为 macOS APFS/TCC 对新 inode 的自然扩展
属性。`copy_xattrs` 已容错这两项差异（与 11.5.0 一致）。三次真实 staging 均为内容/ACL/
mode/owner/group 精确匹配，仅新增 provenance/macl，已不阻断。

验证链路：
1. 首次 `publish`：build → verify-build → publish → 首页登记 → 打开 UI → 播放 → 保存 → 正常退出
2. 热注册验证：第二次 `resume-publish` 返回 `already_registered`
3. 冷重开验证：重启剪映后草稿 `Codex-Build481-Publish-20260923` 仍在首页，可 `verify` 通过
4. 索引 SHA 从原始 `5d206512...` 更新至 `e564f3c9...`，已有草稿和素材均未变化

`tools/audit_publish_metadata.py --runs 3` 只读输入文件，在新的 `work/` 目录比较直接写入、
复制后重写和 APFS clone 后重写的 mode、owner/group、ACL、扩展属性和 SHA-256。
它不把输出指向 live 草稿根、不执行 publish，也不改变 capability。只有一种策略能在隔离夹具
和三次真实登记中稳定保全所有安全元数据，才可提出开启 publish。

本机连续三次非 live 夹具中，直接写入和 APFS clone 均保留了原 quarantine、mode、
owner/group 与空 ACL，但新 inode 都增加 provenance；`copy2` 还重写了 quarantine，
不能采用。该结果仍不足以放行：在真实草稿根的历史暂存中 `macl` 曾出现一次、另一次
未出现，说明 live TCC 路径尚未稳定。三次报告仅保留在忽略的 `work/` 目录。

`tools/audit_publish_live_staging.py --runs 3` 是下一层前置验收：它只在剪映完全退出、
身份精确匹配时创建新的隐藏暂存文件，不替换首页索引、不放置草稿，并保留全部文件和
报告。只有三次的内容、mode、owner/group、ACL 和全部 xattr 都与首页索引精确相等，
才允许继续最小草稿登记；任一差异都在 publish 前停止。

2026-09-23 实际运行结果为 `exact_runs=0/3`：三次均保持内容 SHA、mode、
owner/group、ACL 和原 quarantine，但三次都新增 `com.apple.provenance`。首页索引
本身的 SHA 与 xattr 复核未变，未创建草稿目录、未替换索引。由于前置门槛失败，本轮
没有执行最小草稿登记或 UI 验收，`publish=false` 继续保持。

真实三次验收仍需每轮独立 build、草稿名和 audit，依次完成：首页唯一登记、打开播放、
保存、正常退出、冷启动重开和结构回读。UI 能打开或播放不能替代首页事务证据。

## 阶段 2：existing_edit

状态：`enabled`，`existing_edit=true`（2026-09-23）。

在 publish 链路上叠加验证：
1. 对已 publish 草稿 `Codex-Build481-Publish-20260923`（3 轨：2 视频 + 1 文字 + 1 音频）
   执行只读 `inspect`，源文件 38 个前后 SHA 一致
2. 创建 edit plan：替换文字 + 修改音频音量
3. `build` 成功，`verify-build` 通过
4. `publish` 到首页（新草稿 `Codex-Build481-Edited-20260923`），返回 `created`
5. 源草稿字节不变，四份镜像精确相等，回读 ID 集合严格验证
6. 受限：仅支持单时间线、无云身份、无复合片段/转场/滤镜/蒙版；字体使用系统默认

已知限制：速度修改受计时一致性检查需 extra_material_refs 策略；编辑副本的 tercera
UI 冷重开验收待完善（首轮通过）。
冷重开，本阶段保持 `existing_edit=false`。

## 阶段 3：native_export

状态：`blocked`，`native_export=false`。

只读符号和字符串能确认 Build 481 含 `DraftService::restoreDraft`、`ExportService`、
`exportStart` 与完成事件相关代码，但还不能唯一证明恢复入口、请求构造器、对象大小、
字段偏移、析构路径、response 布局和完成/错误回调 ABI。现有 31 项专项通过只证明
导出在渲染器启动前 fail-closed，不是成片证据。

后续只有在静态位置唯一后，才能用独立子进程、guard page 和 canary 验证最小对象；
随后按基础视频、文字、本地音频三类各连续三次导出，并逐次运行 `ffprobe` 与
`ffmpeg -xerror`。任一异常继续阻断。

## 阶段 4：native_resources

状态：`blocked`，`native_resources=false`。

`doctor` 的 `resource_evidence` 给出字体、字幕、转场、滤镜、特效、贴纸、蒙版、
关键帧、复合片段、调整图层、会员/在线资源三层状态：`offline_build`、
`native_reopen`、`native_export`。该矩阵只描述证据，不能授予运行权限。

当前仅普通字幕的 Build 481 离线层为 `verified`。旧版采集的转场、轻微抖动和六种
蒙版不能直接迁移；已移除的滤镜不恢复；贴纸和调整图层没有实现证据；复合片段保存
持久化已存在明确失败；会员/在线资源不得以缓存存在或技术渲染代替账号和许可证明。

## 每次阶段完成的共同门槛

- 独立 `work/` 夹具和验收报告；源草稿与所有输入媒体前后 SHA-256 一致。
- 全部单元测试、源码清单、`doctor`、`build`、`verify-build` 通过。
- 未解释的字段、资源、扩展属性、ACL、身份、回调或输出差异均失败关闭。
- 本地 `work/`、素材、草稿、日志、codec 和官方二进制不得加入 Git。
