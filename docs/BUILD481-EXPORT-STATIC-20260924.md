# Build 481 arm64 ExportStartReqStruct 静态追踪

日期：2026-09-24
检查对象：`/Applications/VideoFusion-macOS.app/Contents/Frameworks/libvideoeditor.dylib`
SHA-256：`aea79715de6097394c2f38153e11565f02a823678801cd1eafe90bcccb20c086`
方法：`nm -arch arm64`、`dyld_info -arch arm64 -disassemble/-fixups/-exports`、`otool`；未启动 GUI、未附加进程。

## 结论

Build 481 arm64 内部存在一个可被上游代码直接调用的默认初始化函数：文件地址
`0x2681f98`。它与 x86_64 同地址的反汇编不可混为一谈。arm64 的真实调用点先分配
`0x3f0` 字节的 `shared_ptr` 控制块加请求对象，随后将 `this` 指向 `allocation + 0x18`
并直接调用该函数。请求对象大小为 `0x3d8`。这纠正了旧记录把 `0x2681f98` 一概判断为
函数中部、并把 `0x150` 当作完整 `ExportStartReqStruct` 大小的说法。

反汇编、对象 vtable 与回收路径之间的对应关系是完整的：调用方把请求传给导出的
`ExportClient::exportStart(std::shared_ptr<lyra::ExportStartReqStruct>, ...)`；该调用是
同一 dylib 内的直接 `BL`，位于 `0x2681758`。因此 `0x2681f98` 初始化的正是该调用的
请求对象，而不是相邻但不同用途的 `0x150` 字节内部对象。

## 关键指令与对象边界

调用方位于匿名函数 `0x2681568`，关键序列如下：

| 地址 | 观察 | 可确认的含义 |
| --- | --- | --- |
| `0x26815b0` | `mov w0, #0x3f0`; 随后调用 `operator new` | 为组合分配块申请 `0x3f0` 字节 |
| `0x26815c8`–`0x26815d0` | 写控制块 vtable `0x4e42cb0` | shared ownership 控制块起于分配块偏移 0 |
| `0x26815d4`–`0x26815dc` | `this = allocation + 0x18`; `BL 0x2681f98` | 请求对象紧随 24 字节控制块；默认初始化函数只接收 `this` |
| `0x26815e0`–`0x26815e8` | 对 `allocation + 0x60` 执行 `std::string::operator=` | 请求对象 `+0x48` 被赋为调用方传入的字符串 |
| `0x26815ec`–`0x26815f4` | 对 `allocation + 0x78` 调用 `0x1ff1c9c` | 请求对象 `+0x60` 的编译设置子对象被复制 |
| `0x26815f8`–`0x2681604` | 对 `allocation + 0x3d0` 赋固定字符串 | 请求对象 `+0x3b8` 是一个有原生默认值的字符串成员 |
| `0x2681608`–`0x268161c` | 形成 `{object, control}` shared pointer，并从 service 对象读取字段写入 `allocation + 0x50` | 请求对象基类 `tid` 位于 `+0x38` |
| `0x2681744`–`0x2681758` | 直接 `BL ExportClient::exportStart` | 该原生请求沿该调用进入 ExportClient |

`ExportClient::exportStart` 的 arm64 导出符号地址为 `0x103548`。请求类类型名来自其
导出签名；该路径的调用指令是对同镜像地址的直接 `BL`，不是 dyld import stub。

### 对象大小与基类字段

分配总长是 `0x3f0`，请求对象起点为分配块 `+0x18`，因此请求对象大小为
`0x3f0 - 0x18 = 0x3d8`。这与 11.5.0/11.4.2 快照使用的 `0x3d8` 一致。Build 481
完整对象的 vptr 指向 `0x4e42d00`。

已知 `ReqStruct` 基类大小为 `0x48`。结合本机声明及构造/调用方写入，可定位这些字段：

| 请求对象偏移 | 字段 | 依据 |
| --- | --- | --- |
| `+0x00` | vptr | 默认初始化函数写入 `0x4e42d00` |
| `+0x08` | `service` 字符串 | 基类布局；初始化函数写入默认字符串 |
| `+0x20` | `api` 字符串 | 基类布局；初始化函数写入默认字符串 |
| `+0x38` | `tid` | 调用方从 service/session 字段复制到此处 |
| `+0x40` | async 标志 | 初始化函数清零 |
| `+0x44` | flags | 初始化函数清零 |
| `+0x48` | 输出路径字符串 | 调用方执行原生字符串赋值 |
| `+0x60` | 编译设置子对象 | 调用方经 `0x1ff1c9c` 深拷贝 |
| `+0x3b8` | 尾部字符串成员 | 初始化函数构造该成员；调用方将默认字符串写入 |

`0x2681f98` 的函数体使用 x0 作为 `this`、不读取其它参数，写完整对象 vptr 和多个内嵌
字段默认值，并在返回前以 `x0=this` 返回。它调用两次 libc++ 字符串赋值，为继承的两个
字符串成员设置默认 service/api；调用方随后只显式改写路径、设置和 tid。函数中对字段
的偏移写入延伸至 `+0x3d0`，与 `0x3d8` 对象边界相符。

## 编译设置布局

请求的编译设置子对象起于请求对象 `+0x60`，结束于尾部字符串 `+0x3b8` 之前，大小为
`0x358`。调用方将一个完整设置对象通过内部复制函数 `0x1ff1c9c` 复制到该地址；静态
调用点本身没有按字段名称写入 width、height、fps 或 bitrate。

11.5.0/11.4.2 已有 helper 对相同子对象偏移使用如下写入：

| 相对设置对象偏移 | 已有写入 | Build 481 静态结论 |
| --- | --- | --- |
| `+0x3f` | width (`int`) | 位于默认构造清零区域 object `+0x95..+0xa4` |
| `+0x43` | height (`int`) | 位于同一清零区域，和前项紧邻 |
| `+0x47` | 硬件编码偏好 (`byte`) | 构造器在 object `+0xa5` 写 `0x01010000`，故该字节默认值为 1；旧 helper 将它覆写为 0 |
| `+0x4a` | fps (`double`) | 构造器在 object `+0xaa` 写入 `0x403e000000000000`，IEEE-754 值为 30.0 |
| `+0x5e` | bitrate (`long`) | 位于 object `+0xbe..+0xcd` 的默认清零区 |
| `+0x279` | 原生 MP4 writer selector (`byte`) | 位于 object `+0x2d9` 的默认清零区，旧 helper 将其设为 1 |

这些相对偏移与旧版 helper 一致。构造器能证明它们位于相同设置子对象的对应字节/数值
槽位，并且 fps 的存储形态吻合；width、height、bitrate、writer 字节的业务名称仍依赖
旧版字段识别。主 agent 报告的隔离动态试验使用这些旧偏移后得到正确画面、H.264/AAC
输出及完整解码；那项运行时结果补足了静态反汇编本身不能证明的字段语义。

## 析构和最小构造建议

`dyld_info -fixups` 显示请求 vtable 的析构槽：

| vtable 槽地址 | 目标 | 行为 |
| --- | --- | --- |
| `0x4e42d00` (`vtable[0]`) | `0x26822ac` | 完整对象析构，不释放对象内存 |
| `0x4e42d08` (`vtable[1]`) | `0x2682368` | deleting destructor；析构后调用 `operator delete` |

因此与其他版本 helper 一致的 deleter 形式是调用 vtable slot 0 析构对象后再调用
`operator delete(object)`。不要再对同一对象调用 vtable slot 1 后手动释放，以免双重释放。
标准 `std::shared_ptr<ReqStruct>` 的自定义控制块可以管理对象生命周期；不必手造应用的
`0x18` 字节 shared_ptr 控制块布局。

最低限度的 Build 481 请求对象构造候选为：

1. 在进程自己的 C++ 堆中分配 `0x3d8` 字节并做对齐。
2. 以 arm64 image base 加 `0x2681f98` 调用一次原生默认初始化函数，参数只有对象指针。
3. 设置 `ReqStruct::tid`（`+0x38`）、输出 MP4 路径（`+0x48`）和完整编译设置子对象（`+0x60` 起）。保持 `+0x3b8` 的原生默认值。
4. 转成 ABI 兼容的 `std::shared_ptr<lyra::ReqStruct>` 交给 `Server::invokeSync`；由自定义 deleter 调用 vtable slot 0 后释放对象。

此方案有静态证明的构造入口、请求大小、主要成员边界和析构规则；设置字段的 Build 481
语义、响应布局和完成/错误回调仍需独立动态验收。静态结果本身不授权开启正式能力门禁。

## 历史差异说明

`0x2125188` 是另一个内部函数，当前反汇编显示它另外申请 `0x150` 字节对象并基于传入
source shared pointer 做复制路径；它不是这里通过 `ExportClient::exportStart` 传递的
完整 `0x3d8` 请求对象默认初始化入口。以前单看该内部函数而把它当作完整请求布局，会把
默认构造与后续内部复制混淆。
