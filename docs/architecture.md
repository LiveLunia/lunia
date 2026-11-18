# 架构说明

本文记录 Lunia 的当前 NapCat 原型及后续演进方向。事件字段与投递语义见[事件说明](events.md)，运行方法见[开发指南](development.md)。

## 定位与设计原则

Lunia 是面向持续存在的虚拟角色的事件驱动框架，长期定位是陪伴型 Harness。聊天只是角色能够采取的行为之一；角色还可能参与社区、WebUI 交互和游戏。

- **角色唯一性**：角色的行为控制与连续状态由 Actor 管理，不由某个聊天平台、LLM Session 或协议端维持。
- **统一事件空间**：外部环境经 Adapter 转为内部事件，使用共同事件入口；不要求不同领域拥有完全相同的消息结构。
- **感知不等于行动**：事件被接收，不表示角色已经关注、理解或决定回应。角色可以在活动中或休息时继续接收后台事件。
- **依赖方向清晰**：Actor 不直接依赖 NapCat、Discord 等 SDK；通过内部事件、命令、能力接口与外界交互。
- **增量演进**：保留跑通的 MVP，复用成熟库；未来模块先记录职责，不提前创建空目录或引入复杂服务。

## 当前实现

当前 Runtime 直接通过 WebSocket 连接 NapCat。`NapCatClient` 将原始上报交给 `NapCatAdapter`，由 Adapter 调用 Parser 并将内部事件发布到总线。演示消费者通过分类 API 对象发起平台请求。

| 模块 | 当前职责 |
| --- | --- |
| `__main__.py` | `lunia` 命令入口，当前仅输出初始化提示 |
| `adapters/napcat/client.py` | WS 鉴权、接收、重连、`echo` 请求响应关联 |
| `adapters/napcat/adapter.py` | 调用 Parser、隔离单条解析异常、按 `kind` 发布到 EventBus |
| `adapters/napcat/api/` | 消息、群组、用户、文件、系统及其他扩展请求；各分类共享一个 Client |
| `adapters/napcat/parser.py` | 将部分 OneBot 上报解析为内部聊天事件 |
| `adapters/napcat/provider.py` | 按需查询用户资料 |
| `core/events/models.py` | 聊天事件、载荷与消息段类型约定 |
| `core/events/bus.py` | 有界队列、按入队顺序投递、启动与停止 |
| `core/events/dispatcher.py` | 按事件类型管理订阅，同步调用接收者并隔离投递异常 |
| `core/events/consumer.py` | 为单个异步处理器排队，串行处理并记录异常 |
| `core/cache.py` | 用户与会话名称的进程内缓存 |
| `core/runtime.py` | 装配 NapCat 演示，订阅事件并管理总线、消费者的启停 |
| `core/logging.py` | 控制台和文件日志 |
| `resolvers/username.py` | 学习、查询和补全用户显示名称 |
| `resolvers/conversation.py` | 学习与补全会话名称 |
| `formatters/ui.py` | 事件与消息段的终端可读呈现 |
| `tests/manual_*.py` | 与真实 NapCat 联调的手动脚本 |

### 数据流

查看[事件系统架构图](assets/architecture.svg)或下载[可编辑的 Excalidraw 源文件](assets/architecture.excalidraw)。

三个演示消费者分别负责聊天文本显示、命中 `lunia` 的固定回复、被戳后的回戳。聊天文本消费者按需调用 Resolver，缺少用户资料时通过 Provider 查询。每个消费者串行处理自己的队列，名称查询不会阻塞其他消费者。

Client 的同步回调负责解析和入队，接收循环可以继续匹配同一连接的 API 响应。Adapter 记录并跳过单条上报的解析异常，忽略不支持的上报。总线队列满时，`publish` 抛出 `asyncio.QueueFull`，异常会传到 Client 的接收循环。单个接收者的投递异常由 Dispatcher 记录，其余订阅者仍会收到事件。

Runtime 先启动总线和消费者，再运行 Client。Client 退出后，Runtime 先停止总线并排空待投递事件，再等待各消费者处理完队列并停止其任务。消费者在关闭期间仍可能执行需要 NapCat 连接的处理器，此时连接已关闭，相关请求会失败并记录异常。

投递只使用进程内存，队列满时立即拒绝。当前队列按消费者划分，多个消费者之间的处理完成顺序由实际执行决定。缓存为进程内数据，没有过期或容量限制。底层部分 API 返回原始结果，由调用者判断是否成功。

群成员 API 查询的实机验证仍是后续工作。

## 目标工作流

### 入站：外部事件进入角色运行时

```text
QQ / TG / Discord / WebUI / 社区 / 游戏等
    ↓
Adapter（连接与协议转换，保留来源标识）
    ↓ publish
Event Bus（统一入口、有界排队、订阅投递）
    ↓
Actor（角色状态、注意力、行为调度；按需调用其他能力）
```

事件至少需要能定位来源 Adapter **实例**，而不只是协议类型：`adapter_id` 区分例如 `qq-main`、`qq-alt`。聊天事件需要保留会话与消息标识；非聊天事件可以使用自己的领域载荷。并非每条事件都必须进入 Decision 或 LLM。

### 出站：角色发出行为命令

```text
Actor（或当前演示消费者）
    ↓ Command / Action Request
Action Router（按目标实例定位、检查基础能力、返回执行结果）
    ↓
Adapter → Provider → API / SDK → Client
    ↓
外部平台或环境
```

Event 表示**已发生的事实**，Command 表示**希望执行的操作**。内部可以共享消息机制，但语义不同。Actor 可以提出 `ReplyMessage(target, content)`，不需要了解 QQ 的发送 API；Router 依赖命令携带的来源/目标引用找到对应 Adapter，而不是让事件沿原路返回或重新搜索原始消息。需要结果时可以 `await execute(command)`，完成后按需发布成功/失败事件。Router 不应擅自替 Actor 选择其他表达行为。

### Adapter 边界

统一的是 Adapter 的**外部契约**：实例身份、启动/停止生命周期、向总线提交事件、执行支持的命令并报告结果与能力。Adapter 内部不强求相同文件结构。

NapCat 作为 Lunia 的独立 Adapter 长期保留，不将整个目录迁移为通用 OneBot 适配器，也不开发通用 OneBot SDK。其内部允许混用 OneBot 11、go-cqhttp 兼容 API 和 NapCat 扩展。未来 Milky、Discord、Telegram 等分别实现自己的 Adapter，并遵循 Lunia 上层统一契约；这些 Adapter 当前尚未实现。

- NapCat、Milky 可按实际需要组织 Client、Parser、分类 API 和 Provider。
- Telegram、Discord 可直接使用成熟 SDK，无须为目录对称额外手写数百个 API。
- WebUI、社区和游戏也可接入事件；不是所有 Adapter 都必须实现聊天接口。
- Client 可用回调向 Adapter 交付原始事件，但不应直接依赖 Actor、Decision 或具体订阅者。
- Provider 抽象 Lunia 用得上的平台能力，底层 `api/` 可以保留协议专有、领域分类的方法。

### Event Bus 与顺序语义

当前 `EventBus` 已提供统一发布入口、生命周期和有界 FIFO 队列，`EventDispatcher` 负责订阅匹配、同步交付与投递异常隔离。后续可按需要演进队列的顺序域和背压策略。

区分三个顺序：**接收顺序、状态处理顺序、外部行为完成顺序**。同一顺序域（例如同一聊天会话）的顺序敏感消费者应按入队顺序串行处理；不同会话可以并发。非顺序敏感的日志消费者可并行。仅保证 FIFO 出队并不能保证异步处理完成顺序。未来 Actor 仍独立负责回复取消、合并及实际发送调度。队列满时须采用明确的等待/拒绝策略，不应默默丢弃事件。

### Runtime 装配

`Runtime` 负责加载配置、创建 Event Bus、Adapter Registry、Action Router，注入事件发布入口与能力依赖，注册消费者并管理启动和关闭；不负责具体角色决策。QQ 关键词回复与反戳属于演示消费者，应逐步移出 Runtime。

启动大致按：配置 → 核心服务 → Adapter 实例注册 → 消费者订阅 → 总线消费者就绪 → Adapter 启动。关闭时先停止接受新外部事件，再按明确策略排空/取消任务，最后释放连接和资源。连接中断由各 Adapter 管理；Runtime 不依赖 NapCat 的特定类型。

## 下一轮目标项目结构

```text
src/lunia/
├── __main__.py
├── adapters/
│   ├── base.py                 # Adapter 最小契约（新增）
│   ├── registry.py             # Adapter 实例注册（新增）
│   └── napcat/                 # 长期保留的独立 Adapter
│       ├── adapter.py          # 组件组装与生命周期
│       ├── client.py           # 底层通信
│       ├── parser.py           # 协议 → 内部事件
│       ├── provider.py         # 统一能力实现
│       └── api/                # 按功能领域封装混合协议能力
├── core/
│   ├── events/
│   │   ├── models.py           # 内部事件模型（已有）
│   │   ├── bus.py              # 事件入口与生命周期（已有）
│   │   ├── consumer.py         # 异步消费者队列与任务（已有）
│   │   ├── dispatcher.py       # 同步订阅投递（已有）
│   │   └── queue.py            # 顺序域与背压（规划）
│   ├── actions/
│   │   ├── models.py           # Command / Result
│   │   └── router.py           # 找到目标 Adapter 并执行
│   ├── runtime.py              # 平台无关装配
│   ├── cache.py                # 保留
│   └── logging.py              # 保留
├── resolvers/                 # 保留现有 Resolver
└── formatters/                # 保留现有 Formatter
```

## 近期实施与验收

1. **Adapter 整理**：NapCat 独立 Adapter 与分类 API 已整理，调用方统一使用分类对象；后续处理 Adapter 生命周期与 Registry，保留现有收发行为。
2. **Event Bus**：统一 `publish`、有界 FIFO、异常隔离和关闭流程已接入；按会话等顺序域划分队列与扩展背压策略属于后续演进。
3. **Runtime 闭环**：实现最小 Command/Action Router；让演示回复通过目标 Adapter 实例发送；将演示订阅者移出 Runtime，CLI 可以启动 Runtime。

验收重点：原有关键词回复、反戳、名称补全正常；两个 Fake Adapter 同时注册后，来自 A 的消息回复只会到 A；同一顺序域的顺序敏感消费者不会乱序，不同域互不阻塞；单个消费者异常不击穿整个事件系统；启动与关闭能正确释放资源。优先为新增边界补少量针对性自动化测试，避免不相关的全面重构。

## 远期方向

| 名称 | 目标职责 |
| --- | --- |
| Actor | 角色行为与活动的统一调度中心，拥有最终行为控制权 |
| Decision | 在 Actor 请求下快速判断是否行动、选择即时反应等 |
| LLM Harness | 模型调用、上下文、Run、工具循环及中断控制 |
| Experience / Memory | 一条角色经历时间线、按需互动上下文与长期记忆 |
| Game Agent（游戏智能体） | 在 Actor 调度下，通过策略/算法/小模型完成游戏操作，并结合角色偏好与即时互动 |
| WebUI | 以数字房间和聊天为中心的图形界面，兼顾客户端、插件和设置管理 |
| CLI / TUI | 合一的终端管理入口，与 WebUI 共用管理能力 |
| Worker / Nodes | 未来可连接远端算力与游戏设备；唯一主控保留角色状态 |

PS: 这些项目不属于下一轮开发任务
