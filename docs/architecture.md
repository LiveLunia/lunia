# 架构说明

本文描述当前源码的模块关系；长期目标与未实现功能见 [README](../README.md)。

## 当前边界

当前系统是一个 Python 异步 QQ 接入与事件处理原型，直接通过 WebSocket 连接 NapCat，不依赖 AstrBot。内部使用 `ChatEvent` 表达聊天事件，平台协议转换集中在 `adapters/napcat`。

核心长期目标是独立于平台、模型和游戏。当前 `core/runtime.py` 直接导入 NapCat 组件，承担演示组装职责，因此不能将整个 `core/` 目录视为已经完全隔离的平台无关核心。事件定义、分发器和缓存本身没有导入 NapCat。

## 模块职责

| 模块 | 当前职责 |
| --- | --- |
| `src/lunia/__main__.py` | `lunia` 命令入口，仅打印初始化提示 |
| `adapters/napcat/client.py` | WebSocket 鉴权与连接、请求响应匹配、接收事件、重连 |
| `adapters/napcat/api.py` | 将 API 方法参数转换为平台请求，返回完整响应字典 |
| `adapters/napcat/parser.py` | 将支持的 OneBot 上报转换为内部聊天事件 |
| `adapters/napcat/provider.py` | 查询群成员或私聊用户的昵称与别名 |
| `core/events.py` | `TypedDict` 事件、载荷与消息段定义 |
| `core/dispatcher.py` | 按类型维护订阅，为处理器创建异步任务并管理关闭 |
| `core/cache.py` | 用户名称和非私聊会话名称的进程内缓存 |
| `core/runtime.py` | 组装 NapCat 演示运行器并注册消费者 |
| `core/logging.py` | 控制台与文件日志配置 |
| `resolvers/username.py` | 用户名称缓存学习、查询与事件副本补全 |
| `resolvers/conversation.py` | 从事件学习会话名称或从缓存补全 |
| `formatters/ui.py` | 将事件、名称与消息段格式化为可读文本 |
| `tests/manual_*.py` | 连接真实 NapCat 的手动联调工具 |

表内除入口外的模块路径均相对于 `src/lunia/`；测试路径相对于项目根目录。

## 数据流与组装

`Runtime` 创建 `EventDispatcher`、`NapCatClient`、`NapCatAPI`、两类缓存、用户资料 Provider 和两类 Resolver。客户端的事件回调指向 `Runtime.on_event`。

收到 WebSocket 数据后，客户端先区分带 `echo` 的 API 响应与事件上报。API 响应交给对应的等待者；事件上报经 `parse_chat` 解析，支持的事件交给回调，再由分发器按 `kind` 投递。

当前注册三个消费者：

| 消费者 | 订阅 | 行为 |
| --- | --- | --- |
| `on_chat_ui` | 消息、戳一戳、撤回 | 查询用户名称、补全事件副本、格式化并记录日志 |
| `on_message` | 消息 | 跳过自身消息，匹配文本中的 `lunia` 并发送固定回复 |
| `on_poke` | 戳一戳 | 仅对其他用户戳当前账号的事件回戳 |

各消费者并发处理。名称查询可能等待 API，但不会成为其他消费者处理事件的前置条件。

## Resolver 与缓存

Resolver 是辅助组件，不参与总线的固定流水线，也不负责再次投递事件。调用者决定是否需要名称补全；当前调用者是 `on_chat_ui`。

`UserNameResolver.fetch_missing` 检查事件操作者在缓存中的昵称与别名，任一缺失时通过 `UserInfoProvider` 查询，并填补缓存缺项。群聊 Provider 调用 `get_group_member_info`，私聊调用 `get_stranger_info`。它只主动查询操作者，不逐个查询戳一戳目标或被撤回消息的发送者。

`UserNameResolver.resolve` 从当前事件学习操作者名称，再补全返回副本中的操作者，以及戳一戳目标或撤回消息发送者的缓存名称。需要修改载荷时会复制载荷。`ConversationResolver.resolve` 从事件学习会话名称，缺失时读取缓存；它没有群资料 API 查询能力。

用户缓存键包含平台、登录账号、会话类型、会话 ID 和用户 ID；会话缓存键不包含用户 ID。缓存仅存在于内存，没有持久化、过期机制或容量限制。别名持续缺失时，后续事件仍可能触发用户资料查询。

## 运行与关闭

客户端用唯一 `echo` 关联请求，默认等待 API 响应 10 秒；连接中断时使待完成请求失败，随后每隔 3 秒尝试重新连接。重连不负责重发已失败的 API 请求。

分发器为每个订阅处理器创建任务，任务结束时记录异常。`Runtime.run` 退出时调用分发器关闭：默认等待 5 秒，然后取消剩余任务。它没有事件队列、背压、持久化投递或重试机制，也不保证处理完成顺序。

## 当前限制

事件类型标注不会在运行时自动校验所有上游字段。解析器只处理已有分支；消息上报要求消息段数组。API 封装通常返回原始响应，由调用方判断平台操作是否成功；用户资料 Provider 会检查状态、返回码与数据形状。

源码依据：[运行器](../src/lunia/core/runtime.py)、[客户端](../src/lunia/adapters/napcat/client.py)、[分发器](../src/lunia/core/dispatcher.py)、[用户名称补全](../src/lunia/resolvers/username.py)、[会话名称补全](../src/lunia/resolvers/conversation.py)。
