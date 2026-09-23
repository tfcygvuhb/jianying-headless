# 剪映 11.4.0 Build 481 分阶段验收

本页只适用于精确运行档案 `jy14-headless-macos-11.4.0-build481`。它记录证据，
不因为某项离线测试通过而自动开启能力。应用签名、Team ID、动态库和 codec 哈希仍由
`doctor` 每次重新核对。

## 当前结论

| 分类 | 结果 |
| --- | --- |
| 已验证 | 精确应用身份；profile 专用 codec；基础视频、普通文字和本地音频的离线 `build` / `verify-build`；所有禁用能力的 fail-closed 门禁 |
| 部分验证 | 普通字幕只有离线构建证据；真实素材曾在 UI 导入和播放，但不构成无界面 publish、保存回读或原生导出证据 |
| 未验证 | Build 481 的本地字体、关键帧、贴纸、调整图层；所有项目的三次独立原生验收；原生导出 ABI 与成片 |
| 明确阻断 | `publish` 受首页索引扩展属性差异阻断；`existing_edit` 依赖尚未通过的 publish；转场、滤镜、特效、蒙版和在线资源受版本来源或许可证据阻断；复合片段受保存持久化问题阻断 |

## 阶段 1：publish

状态：`blocked`，`publish=false`。

已确认首页索引原件带有 `com.apple.quarantine`。在当前 macOS/TCC 环境中，新建暂存
inode 会自然出现 `com.apple.provenance`，部分试验还出现 72 字节
`com.apple.macl`。现有事务在替换首页索引前拒绝，未把目标草稿登记到首页。

`tools/audit_publish_metadata.py --runs 3` 只读输入文件，在新的 `work/` 目录比较直接写入、
复制后重写和 APFS clone 后重写的 mode、owner/group、ACL、扩展属性和 SHA-256。
它不把输出指向 live 草稿根、不执行 publish，也不改变 capability。只有一种策略能在隔离夹具
和三次真实登记中稳定保全所有安全元数据，才可提出开启 publish。

本机连续三次非 live 夹具中，直接写入和 APFS clone 均保留了原 quarantine、mode、
owner/group 与空 ACL，但新 inode 都增加 provenance；`copy2` 还重写了 quarantine，
不能采用。该结果仍不足以放行：在真实草稿根的历史暂存中 `macl` 曾出现一次、另一次
未出现，说明 live TCC 路径尚未稳定。三次报告仅保留在忽略的 `work/` 目录。

真实三次验收仍需每轮独立 build、草稿名和 audit，依次完成：首页唯一登记、打开播放、
保存、正常退出、冷启动重开和结构回读。UI 能打开或播放不能替代首页事务证据。

## 阶段 2：existing_edit

状态：`blocked`，`existing_edit=false`。

现有实现能复制整个单时间线草稿、按 ID 修改已知字段，并核对源文件清单；Build 481
尚无正式 edit CLI 验收通道，也没有三份独立副本的保存冷重开证据。publish 未通过前，
不执行 live 副本登记。首个夹具必须排除云身份、复合片段、在线资源、转场和效果缓存，
并在操作前后核对原草稿、外部媒体和副本资源 SHA-256。

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
