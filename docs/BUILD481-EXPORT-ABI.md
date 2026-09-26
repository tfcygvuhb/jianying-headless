# Build 481 arm64 导出 ABI 逆向结论（2026-09-24）

## 已确认可用的链路

### 1. DraftService::restoreDraft（已完成）
- arm64 实现：`FUN_02041b80` = `DraftService::restoreDraft(shared_ptr<ReqStruct>)`
- 通过 `Server::invoke` 派发 `{"DraftService","restoreDraft"}` 即可触发
- 日志确认：`restoreDraft:605 → restoreDraft:1208 → operator():669 (driverRun callback)` + `JY_NATIVE_RESTORE_DONE`
- helper 已改为 invoke 派发，restore 阶段完全工作

### 2. ExportService::exportStart 路由（已打通）
- 轻量 `ReqStruct{service="ExportService", api="exportStart", tid}` 通过 `Server::invokeSync` 可到达 `ExportService::exportStarts`（日志 `exportStart:28`）
- 崩溃发生在 ExportService 内部从请求深拷贝构造完整 ExportStartReqStruct 时

## 尚未解决：ExportStartReqStruct 构造

- arm64 构造器：`FUN_02125188`（0x150 字节深拷贝构造，非无参构造）
- 它要求源 x1 是已实例化的 ExportStartReqStruct；裸 storage 或轻量 req 都会在
  深拷贝 vector/string 时崩溃（`FUN_01feff70 → std::string copy`）
- `0x1148290` 实测是 `MaterialVideo::deep_copy_raw`（LLDB 确认），不是构造器
- x86_64 的 `0x2681f98` 也是函数中部地址（`incq (%rcx)`），不是无参构造入口

## 需要的下一步
1. 找到 `ExportStartReqStruct` 的无参/默认构造（可能由 ExportService 内部工厂创建）
2. 或通过剪映 GUI 调用 exportStart 时用 LLDB 捕获已构造 req 的内存布局
3. request_size 在 arm64 为 0x150（336），不是 x86 的 0x3d8
