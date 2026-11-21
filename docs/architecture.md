# 架构说明

本文记录 Lunia 当前已实现的 NapCat 事件流、最小行动路由与 LLM 接入，以及后续演进方向。事件字段与投递语义见[事件说明](events.md)，运行方法见[开发指南](development.md)。

## 定位与设计原则

Lunia 是面向持续存在的虚拟角色的事件驱动框架，长期定位是陪伴型 Harness。聊天只是角色能够采取的行为之一；角色还可能参与社区、WebUI 交互和游戏。

- **角色唯一性**：角色的行为控制与连续状态将由 `Actor` 管理，不由某个聊天平台、LLM Session 或协议端维持。
- **统一事件空间**：外部环境经 Adapter 转为内部事件并包装为 `EventEnvelope`，使用共同事件入口；不要求不同领域拥有完全相同的消息结构。
- **感知不等于行动**：事件被接收，不表示角色已经关注、理解或决定回应。角色可以在活动中或休息时继续接收后台事件。
- **依赖方向清晰**：未来 `Actor` 不直接依赖 NapCat、Discord 等 SDK；通过内部事件、命令、能力接口与外界交互。
- **增量演进**：保留跑通的 MVP，复用成熟库；未来模块先记录职责，不提前创建空目录或引入复杂服务。

## 当前实现

当前 `Runtime` 装配单个 `NapCatAdapter` 实例（`adapter_id="main"`）、事件总线与分发器、名称缓存与 Resolver、`ActionRouter`、`LLMManager` 及三个异步消费者。`NapCatAdapter` 内部持有并管理 `NapCatClient`、`NapCatAPI` 与 `NapCatMessageProvider`，将原始上报经 `parser.py` 转为 `ChatEvent`，包装为 `EventEnvelope` 后发布到 `EventBus`。

| 模块 | 当前职责 |
| --- | --- |
| `__main__.py` | `lunia` 命令入口，当前仅输出初始化提示 |
| `adapters/napcat/client.py` | WebSocket Bearer 鉴权、接收循环、断线重连、`echo` 请求响应关联 |
| `adapters/napcat/parser.py` | 将部分 OneBot 上报解析为内部 `ChatEvent`（消息、戳一戳、撤回） |
| `adapters/napcat/adapter.py` | 持有 Client / API / `NapCatMessageProvider`，管理 Client 生命周期（`start`/`run`/`stop`），隔离解析异常，包装 `EventEnvelope` 并发布到 `EventBus` |
| `adapters/napcat/api/` | 消息、群组、用户、文件、系统及其他扩展共 6 类 108 个异步方法；各分类共享一个 `NapCatClient` |
| `adapters/napcat/provider.py` | `NapCatUserProvider`（按需查询用户资料）与 `NapCatMessageProvider`（实现 `MessageProvider`，经 `api.message.send_msg` 发消息） |
| `core/events/models.py` | `ChatEvent`、`LuniaEvent`、消息段类型约定，以及携带 `adapter_id` 的 `EventEnvelope` |
| `core/events/bus.py` | 有界 FIFO 队列（默认 1024）、非阻塞 `publish() -> bool`（满队拒收并计数）、工作任务存活检查、带超时排空关闭 |
| `core/events/dispatcher.py` | 按事件类型管理订阅，同步调用 `EventReceiver` 并隔离投递异常 |
| `core/events/consumer.py` | `AsyncConsumer` 为单个异步处理器维护有界 `mailbox`（默认 256），串行处理并记录异常 |
| `core/actions/models.py` | 最小行动模型 `SendMessage` |
| `core/actions/router.py` | `MessageProvider` 协议与 `ActionRouter`，按 `adapter_id` 注册、注销并执行 `SendMessage` |
| `llm/config.py`、`llm/types.py` | `ProviderConfig`、`ModelConfig`、`Message`、`Usage`、`LLMRequest`、`LLMResponse` 数据结构 |
| `llm/manager.py` | `LLMManager` 管理模型别名与 Provider 客户端路由，以及统一 `close()` |
| `llm/protocols/openai.py` | 基于 `openai.AsyncOpenAI` 的 `OpenAICompatibleClient`（超时 30s，重试 1 次） |
| `demo/chat.py` | 临时单轮 LLM 对话消费者 `ChatDemo`，串联 `LLMManager` 与 `ActionRouter` |
| `core/cache.py` | `UserNameCache` 与 `ConversationCache` 进程内缓存 |
| `core/runtime.py` | 装配上述组件、订阅事件并管理总线与消费者的启停 |
| `core/logging.py` | 控制台彩色日志（`INFO+`）和 `logs/lunia.log` 文件日志（`DEBUG+`） |
| `resolvers/username.py` | 学习、查询（经 `UserInfoProvider`）和补全用户显示名称 |
| `resolvers/conversation.py` | 学习与补全非私聊会话名称 |
| `formatters/ui.py` | 事件与消息段的终端可读呈现 |
| `tests/manual_*.py` | 与真实 NapCat 联调的手动脚本 |

### 数据流

查看[架构图](assets/architecture.svg)或下载[可编辑的 Excalidraw 源文件](assets/architecture.excalidraw)。

- **入站链路**：`NapCatClient._receive_loop()` 解码 WebSocket JSON 并按 `echo` 分流（带 `echo` 唤醒 `call_api()` Future，其余同步回调 `NapCatAdapter.on_event()`）。`NapCatAdapter` 调用 `parse_chat()` 解析上报、隔离单条解析异常并跳过不支持的上报，构造 `EventEnvelope(adapter_id=self.adapter_id, event=event)` 后调用 `EventBus.publish(event["kind"], envelope)`。`EventBus` 按入队顺序出队交由 `EventDispatcher.dispatch()` 同步投递给订阅者；单个接收者的投递异常由 Dispatcher 记录，其余订阅者仍会收到事件。
- **三路消费者与出站**：三个 `AsyncConsumer` 各自在独立异步任务中串行处理自己的 `mailbox`，彼此并发互不阻塞：
  - `chat_consumer` -> `Runtime.on_chat_ui`（订阅 `chat.message`、`chat.poke`、`chat.recall`）：按需调用 `UserNameResolver.fetch_missing()`（仅补查 `actor_id` 缺失资料，经 `NapCatUserProvider` -> `NapCatAPI` 查询）及 `UserNameResolver.resolve()` / `ConversationResolver.resolve()`，随后经 `format_chat_event()` 输出日志。
  - `message_consumer` -> `ChatDemo.handle`（订阅 `chat.message`）：过滤自身消息、无 `adapter_id` 或空文本消息；群聊要求文本含 `lunia`（不区分大小写），私聊仅响应 `conversation_id == TEST_QQ`。命中后发起单轮 `LLMRequest(model="chat", ...)`，经 `LLMManager` -> `OpenAICompatibleClient` 获取回复，再构造 `SendMessage` 交由 `ActionRouter` -> `NapCatMessageProvider` -> `NapCatAPI.message.send_msg()` 发回来源 Adapter。
  - `poke_consumer` -> `Runtime.on_poke`（订阅 `chat.poke`）：当 `target_id == account_id` 且操作者不是自己时，当前仍直接调用 `self.adapter.api.message.send_poke()`，尚未经过 `ActionRouter`。
- **启停与当前限制**：
  - `Runtime.run()` 先启动总线与三个消费者，再执行 `await adapter.start()` 和 `await adapter.run()`。进入 `finally` 后，先执行 `await bus.stop()`（默认超时 5s 排空待投递事件），再等待三个消费者排空各自 `mailbox` 并停止其任务。当前 `finally` 尚未显式调用 `adapter.stop()` 与 `llm.close()`；连接关闭后消费者排空期间依赖 NapCat 连接的请求可能失败并记录异常。
  - `EventBus` 队列满时非阻塞拒收（`publish()` 累加 `dropped_events`、限频记录警告并返回 `False`）；总线未运行或投递任务异常退出时，`publish()` 抛出 `RuntimeError` 并传至 Client 接收循环。
  - `Runtime.__init__()` 当前硬编码了 NapCat 地址（`ws://127.0.0.1:3799`）与 DeepSeek LLM 配置（`https://api.deepseek.com`、`model_id="deepseek-flash"`），并从进程环境读取 `NAPCAT_TOKEN` 与 `DEEPSEEK_API_KEY`；`demo/chat.py` 在模块导入期直接读取 `TEST_QQ`。
  - 队列与缓存均在进程内存中，缓存没有过期或容量限制；多个消费者之间的处理完成顺序由实际执行决定。底层部分 API 返回原始结果，由调用者判断是否成功。
  - 群成员 API 查询等接口的实机验证仍是后续工作。

## 目标工作流

### 入站：外部事件进入角色运行时

```text
QQ / TG / Discord / WebUI / 社区 / 游戏等
    ↓
Adapter（连接与协议转换，包装携带 adapter_id 的 EventEnvelope）
    ↓ publish
EventBus + EventDispatcher（统一入口、有界排队、订阅投递）
    ↓
Actor（尚未实现：角色状态、注意力、行为调度；按需调用其他能力）
```

事件通过 `EventEnvelope.adapter_id` 定位来源 Adapter **实例**（例如 `qq-main`、`qq-alt`），而不只是协议类型。聊天事件保留会话与消息标识；非聊天事件可使用自己的领域载荷。并非每条事件都必须进入 Decision 或 LLM。

### 出站：角色发出行为命令

```text
Actor（尚未实现；当前为 ChatDemo 演示消费者）
    ↓ Command / Action Request（当前已实现 SendMessage）
ActionRouter（按目标实例定位并执行）
    ↓
Adapter → Provider → API / SDK → Client
    ↓
外部平台或环境
```

Event 表示**已发生的事实**，Command / Action 表示**希望执行的操作**。内部可以共享消息机制，但语义不同。`ActionRouter` 依赖行动携带的 `adapter_id` 找到已注册的目标 Provider，而不是让事件沿原路返回或重新搜索原始消息。需要结果时 `await execute(action)`；Router 不应擅自替 Actor 选择其他表达行为。当前仅实现 `SendMessage` 与原始 `dict` 返回值，统一结果结构及更多行动类型留待按需扩展。

### Adapter 边界

统一的是 Adapter 的**外部契约**：实例身份、启动/停止生命周期、向总线提交 `EventEnvelope`、执行支持的命令并报告结果与能力。Adapter 内部不强求相同文件结构。

NapCat 作为 Lunia 的独立 Adapter 长期保留，不将整个目录迁移为通用 OneBot 适配器，也不开发通用 OneBot SDK。其内部允许混用 OneBot 11、go-cqhttp 兼容 API 和 NapCat 扩展。未来 Milky、Discord、Telegram 等分别实现自己的 Adapter，并遵循 Lunia 上层统一契约；这些 Adapter 当前尚未实现。

- NapCat、Milky 可按实际需要组织 Client、Parser、分类 API 和 Provider。
- Telegram、Discord 可直接使用成熟 SDK，无须为目录对称额外手写数百个 API。
- WebUI、社区和游戏也可接入事件；不是所有 Adapter 都必须实现聊天接口。
- Client 通过同步回调向 Adapter 交付原始事件，但不应直接依赖 Actor、Decision 或具体订阅者。
- Provider 抽象 Lunia 用得上的平台能力，底层 `api/` 可以保留协议专有、领域分类的方法。

### EventBus 与顺序语义

当前 `EventBus` 已提供统一发布入口、工作任务存活检查、满队计数拒收与带超时排空关闭，`EventDispatcher` 负责订阅匹配、同步交付与投递异常隔离。后续可按需要演进队列的顺序域和背压策略。

区分三个顺序：**接收顺序、状态处理顺序、外部行为完成顺序**。同一顺序域（例如同一聊天会话）的顺序敏感消费者应按入队顺序串行处理；不同会话可以并发。非顺序敏感的日志消费者可并行。仅保证 FIFO 出队并不能保证异步处理完成顺序。未来 Actor 仍独立负责回复取消、合并及实际发送调度。队列满时须采用明确的等待/拒绝策略，不应默默丢弃事件。

### Runtime 装配

目标方向是让 `Runtime` 负责加载配置、创建 EventBus、Adapter 管理与 ActionRouter，注入事件发布入口与能力依赖，注册消费者并管理启动和关闭；不负责具体角色决策。当前 QQ 演示消费者与硬编码配置仍位于 `Runtime` 与 `demo/` 中，待后续逐步解耦。

启动大致按：配置 → 核心服务 → Adapter 实例注册 → 消费者订阅 → 总线与消费者就绪 → Adapter 启动。关闭时先停止接受新外部事件，再按明确策略排空/取消任务，最后释放连接、HTTP 客户端和资源。连接中断由各 Adapter 管理；长期目标是 Runtime 不依赖 NapCat 的特定类型。

## 演进结构对照

以下对照当前已实现文件与仍在规划中的位置（规划项尚未创建，不代表已定稿）：

```text
src/lunia/
├── __main__.py                 # CLI 入口（已有；当前仅输出初始化提示）
├── adapters/
│   ├── base.py                 # Adapter 最小契约（规划，未实现）
│   ├── registry.py             # Adapter 实例注册（规划，未实现）
│   └── napcat/                 # 长期保留的独立 Adapter（已有）
│       ├── adapter.py          # 组件组装、EventEnvelope 包装与生命周期
│       ├── client.py           # 底层通信与 echo 关联
│       ├── parser.py           # 协议 → ChatEvent
│       ├── provider.py         # UserProvider 与 MessageProvider
│       └── api/                # 按功能领域封装混合协议能力
├── core/
│   ├── events/
│   │   ├── models.py           # ChatEvent / LuniaEvent / EventEnvelope（已有）
│   │   ├── bus.py              # 有界队列、满队拒收与超时关闭（已有）
│   │   ├── consumer.py         # AsyncConsumer 异步消费者队列与任务（已有）
│   │   ├── dispatcher.py       # 同步订阅投递与异常隔离（已有）
│   │   └── queue.py            # 顺序域与背压（规划，未实现）
│   ├── actions/
│   │   ├── models.py           # SendMessage 行动模型（已有）
│   │   └── router.py           # MessageProvider 协议与 ActionRouter（已有）
│   ├── runtime.py              # 当前装配 NapCat + LLM + Demo（待解耦平台与配置）
│   ├── cache.py                # 保留（已有）
│   └── logging.py              # 保留（已有）
├── llm/                        # 最小模型管理与 OpenAI 兼容客户端（已有）
│   ├── config.py
│   ├── types.py
│   ├── manager.py
│   └── protocols/openai.py
├── demo/
│   └── chat.py                 # 临时单轮 LLM 对话演示（已有，正在演进）
├── resolvers/                  # 保留现有 Resolver（已有）
└── formatters/                 # 保留现有 Formatter（已有）
```

## 近期实施状态与验收重点

1. **已落地能力**：NapCat 独立 Adapter 与分类 API、Client 生命周期与 `EventEnvelope` 封装、`EventBus` 满队拒收与带超时关闭、最小 `ActionRouter` + `SendMessage` 路由、最小 `LLMManager` + `OpenAICompatibleClient`，以及 `ChatDemo` 单轮对话演示链路。
2. **待收敛与后续方向**：
   - 整理 `Runtime` / `ChatDemo` 的环境变量配置注入与退出清理，同步更新 `tests/test_runtime.py`，并使 `lunia` CLI 入口可启动 Runtime。
   - 按实际多 Adapter 与多行动需求，再评估 `adapters/base.py`、`adapters/registry.py`、非文本行动（如戳一戳）及按会话顺序域划分队列（`core/events/queue.py`）。

验收重点：对话回复、反戳、名称补全正常；两个 Fake Adapter 同时注册后，来自 A 的消息回复只会路由到 A；同一顺序域的顺序敏感消费者不会乱序，不同域互不阻塞；单个消费者异常不击穿整个事件系统；启动与关闭能正确释放连接与客户端资源。优先为新增边界补少量针对性自动化测试，避免不相关的全面重构。

## 远期方向（均未实现）

| 名称 | 目标职责 |
| --- | --- |
| Actor | 角色行为与活动的统一调度中心，拥有最终行为控制权 |
| Decision | 在 Actor 请求下快速判断是否行动、选择即时反应等 |
| LLM Harness | 在现有 `llm/` 之上构建上下文、Run、工具循环及中断控制 |
| Experience / Memory | 一条角色经历时间线、按需互动上下文与长期记忆 |
| Game Agent（游戏智能体） | 在 Actor 调度下，通过策略/算法/小模型完成游戏操作，并结合角色偏好与即时互动 |
| WebUI | 以数字房间和聊天为中心的图形界面，兼顾客户端、插件和设置管理 |
| CLI / TUI | 合一的终端管理入口，与 WebUI 共用管理能力 |
| Worker / Nodes | 未来可连接远端算力与游戏设备；唯一主控保留角色状态 |

PS: 这些项目不属于近期开发任务
