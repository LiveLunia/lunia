# 更新日志

Lunia 的重要功能更新与变更记录。

本项目采用 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 风格组织更新日志。

## [未发布]

### 新增

- NapCat WebSocket 客户端，支持 Bearer 鉴权、断线重连、通过 `echo` 匹配 API 响应、请求超时及断线时清理待完成请求。
- NapCat API 调用封装，涵盖消息、用户、群组、文件、系统及扩展接口共 108 个方法；封装范围不代表实机验证范围。
- QQ 私聊与群聊的统一聊天事件结构（`ChatEvent` / `LuniaEvent`）与携带 `adapter_id` 的 `EventEnvelope`，解析消息、戳一戳、私聊撤回和群聊撤回。
- 文本、提及、引用、图片、语音、视频、合并转发、JSON 卡片消息段解析，以及未知消息段的原始数据保留。
- 进程内事件总线 `EventBus` 与同步分发器 `EventDispatcher`，支持有界 FIFO 投递、满队非阻塞拒收与 `dropped_events` 计数、后台投递任务健康检查及带超时排空关闭。
- 最小行动路由模块 `core/actions/`（`SendMessage`、`MessageProvider`、`ActionRouter`）及 `NapCatMessageProvider`，支持按 `adapter_id` 路由出站消息。
- 最小 LLM 调用模块 `llm/`（`ProviderConfig`、`ModelConfig`、`LLMRequest`、`LLMResponse`、`LLMManager` 及基于 `openai.AsyncOpenAI` 的 `OpenAICompatibleClient`）。
- 临时单轮 LLM 对话演示 `demo/chat.py`（`ChatDemo`），在群聊命中 `lunia` 或私聊匹配 `TEST_QQ` 时调用 `LLMManager` 并经 `ActionRouter` 回复。
- 按平台、账号和会话隔离的用户名称与会话名称内存缓存，以及按需调用的 `UserNameResolver`、`ConversationResolver` 与 `NapCatUserProvider`。
- NapCat 演示 `Runtime`，组装 Adapter、事件总线、缓存、Resolver、`ActionRouter`、`LLMManager` 与异步消费者，并支持忽略自身消息与被戳回戳等演示行为。
- 聊天事件的终端可读文本格式化，以及控制台彩色日志和文件日志。
- 连接/API、事件接收、聊天文本显示及交互式 API 控制台手动联调脚本。
- 基于 uv 的项目与依赖配置（`websockets`、`openai`、Ruff、pytest），以及仅输出初始化提示的 `lunia` 命令入口。
- 简体中文项目说明、架构说明、事件说明及开发指南。
- 覆盖事件总线、行动路由、LLM 管理、分类 API 及 Runtime 流程的离线自动化测试。

### 变更

- 将事件模型迁至 `core/events/models.py`，引入 `EventEnvelope` 携带来源 `adapter_id`；分发器按事件类型同步调用 `EventReceiver`，异步处理由 `AsyncConsumer` 各自管理。
- `NapCatAdapter` 封装 `NapCatClient` 生命周期（`start` / `run` / `stop`）、`NapCatAPI` 与 `NapCatMessageProvider`。
- `EventBus.publish()` 队列满时改为计数并记录限频警告后返回 `False`，不再抛出 `asyncio.QueueFull`；`EventBus.stop()` 增加超时控制与异常退出检测。
- 将 108 个 NapCat API 方法组织为消息、群组、用户、文件、系统及其他扩展六个分类，共享同一个 Client，调用方统一使用分类对象。
- NapCat 明确作为长期独立 Adapter 保留，取消整体迁移为通用 OneBot 适配器的规划。
- `Runtime` 消息消费者由固定关键词回复（“检测到关键词”）切换为 `ChatDemo` 单轮 LLM 对话演示。

### 修复

- 单条上报解析失败时记录错误并继续接收，不再让解析异常终止客户端连接循环。
- Runtime 随正式包加载异步消费者，退出时先排空事件总线，再等待消费者处理队列并停止任务。
- `EventBus.stop()` 在投递任务异常退出或排空超时时及时失败并回收任务，避免无限阻塞。
- 将离线测试及事件、聊天文本联调脚本迁移到 `NapCatAdapter`、`EventEnvelope` 及新的启停流程。
