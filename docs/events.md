# 事件说明

内部事件与信封定义见 [`core/events/models.py`](../src/lunia/core/events/models.py)，QQ 转换逻辑见 [`adapters/napcat/parser.py`](../src/lunia/adapters/napcat/parser.py)。`TypedDict` 用于描述聊天事件字典结构，`EventEnvelope` 使用不可变 `dataclass` 包装来源元信息。

## 事件包装：`EventEnvelope` 与 `LuniaEvent`

当前 `LuniaEvent` 类型别名为 `ChatEvent`。Adapter 将解析后的事件包装为 `EventEnvelope` 后再投递至总线，以便下游消费者识别事件来自哪一个 Adapter 实例：

```python
@dataclass(frozen=True, slots=True)
class EventEnvelope:
    event: LuniaEvent
    adapter_id: str | None = None
```

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `event` | `LuniaEvent` | 内部事件对象（当前为 `ChatEvent`） |
| `adapter_id` | `str \| None` | 来源 Adapter 实例标识（例如 `NapCatAdapter` 传入的 `"main"`）；缺省为 `None` |

下游需要回发消息时（如 `ChatDemo`），通过 `envelope.adapter_id` 构造 `SendMessage` 交由 `ActionRouter` 路由回原 Adapter 实例。

## 公共字段（`ChatEventBase`）

所有 `ChatEvent` 都包含以下字段，名称字段在无法获得时为 `None`：

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `kind` | 事件类型字面量 | `chat.message`、`chat.poke` 或 `chat.recall` |
| `platform` | `Platform` | 来源平台；当前解析器固定为 `qq` |
| `account_id` | `str` | 当前登录账号 ID |
| `conversation_type` | `ConversationType` | 会话类型；当前解析器输出 `private` 或 `group` |
| `conversation_id` | `str` | 群聊为群 ID，私聊为上报中的用户 ID |
| `conversation_name` | `str \| None` | 群名称；当前私聊解析结果为 `None` |
| `actor_id` | `str \| None` | 事件操作者 ID |
| `actor_name` | `str \| None` | 操作者昵称 |
| `actor_alias` | `str \| None` | 操作者群名片或私聊备注 |
| `timestamp` | `int` | 上游 `time` 字段 |
| `payload` | 对应载荷 | 由 `kind` 决定的事件专属数据 |

`Platform` 还预留 `wechat`、`telegram`、`discord`、`web`、`cli`，`ConversationType` 还预留 `channel`；它们只是类型取值，不代表已有适配器。当前解析器将各类 ID 转成字符串，并根据是否存在 `group_id` 判断群聊。

## 事件类型与载荷

### 消息：`chat.message`

对应 `post_type == "message"`，操作者为消息发送者。载荷包含 `message_id: str` 和 `segments: list[MessageSegment]`。昵称来自 `sender.nickname`，别名取群聊 `sender.card` 或私聊 `sender.remark`。

`parse_segments` 处理消息段数组，不解析字符串形式的 CQ 码。

| 内部消息段 | 字段 | 当前转换行为 |
| --- | --- | --- |
| `text` | `text: str` | 文本内容 |
| `at` | `target_id: str` | 来自 `data.qq`，`all` 表示全体成员 |
| `reply` | `message_id: str` | 被引用消息 ID |
| `image` | `file`、`url` | 可空字符串，保留媒体定位信息 |
| `record` | `file`、`url`、`path` | 可空字符串，保留语音定位信息 |
| `video` | `file`、`url` | 可空字符串，保留视频定位信息 |
| `forward` | `forward_id: str` | 合并转发 ID，不展开内容 |
| `json` | `data: str \| dict[str, object]` | 保留 JSON 卡片内容 |
| `unknown` | `original_type: str`、`data: dict[str, object]` | 保留未识别类型及其原始数据 |

JSON 卡片内容既非字符串也非字典时，转换为 `original_type == "json"` 的未知消息段。媒体消息段的结构保留不包含下载、识别或理解媒体内容。

### 戳一戳：`chat.poke`

对应 `post_type == "notice"`、`notice_type == "notify"`、`sub_type == "poke"`。操作者来自 `user_id`。

| 载荷字段 | 类型 | 含义 |
| --- | --- | --- |
| `target_id` | `str` | 被戳用户 |
| `target_name`、`target_alias` | `str \| None` | 解析时为 `None`，可从缓存补全 |
| `action_text` | `str` | `raw_info` 中首个 `nor` 文本；缺失时为“戳了戳” |
| `suffix_text` | `str` | 其余 `nor` 文本拼接结果 |

### 撤回：`chat.recall`

对应 `post_type == "notice"` 且 `notice_type` 为 `group_recall` 或 `friend_recall`。群聊操作者取 `operator_id`，私聊操作者与原发送者均取 `user_id`。

| 载荷字段 | 类型 | 含义 |
| --- | --- | --- |
| `message_id` | `str` | 被撤回的消息 ID |
| `sender_id` | `str \| None` | 原消息发送者；当前解析器从 `user_id` 转换 |
| `sender_name`、`sender_alias` | `str \| None` | 解析时为 `None`，可从缓存补全 |

撤回事件不携带原消息正文，当前没有消息历史存储或正文恢复功能。

## 从上报到消费者

1. `NapCatClient` 将 JSON 解码为字典；非法 JSON 会记录警告并跳过。
2. `echo` 不为 `None` 的数据作为 API 响应唤醒对应 Future，不送入聊天解析器。
3. 其余数据通过同步回调交给 `NapCatAdapter.on_event`，由 Adapter 调用 `parse_chat`。解析异常会记录并跳过；不支持的上报（包括心跳和其他通知）返回 `None`，不投递聊天事件。
4. Adapter 构造 `EventEnvelope(adapter_id=self.adapter_id, event=event)`，调用 `EventBus.publish(event["kind"], envelope)`，同步尝试将 `(event_type, envelope)` 放入总线队列；返回 `False` 时记录调试日志。
5. 总线后台任务 `lunia-event-bus` 按入队顺序调用 `EventDispatcher.dispatch(event_type, envelope)`。分发器快照当前订阅列表，按注册顺序同步调用 `EventReceiver` 回调并交付同一个 `EventEnvelope` 对象。
6. `Runtime` 中的 `AsyncConsumer.receive(envelope)` 将信封放入各自的 `mailbox`（默认容量 256）。每个消费者在独立异步任务中串行等待处理器完成，不同消费者可并发执行。

聊天文本消费者（`Runtime.on_chat_ui`）按需调用 `UserNameResolver`（其中 `fetch_missing` 仅补查 `actor_id` 的缺失资料，`resolve` 同时从缓存补全戳一戳目标和撤回原发送者）与 `ConversationResolver`，并使用补全后的事件副本；`ChatDemo` 与 `Runtime.on_poke` 直接读取 `envelope.event`（`ChatDemo` 同时使用 `envelope.adapter_id` 进行出站路由）。处理器应把原始事件字典视为只读，因为多个订阅者共享同一份对象。

### 队列、异常与停止

- **总线入队与满队处理**：总线队列默认容量为 `1024`。`publish()` 为非阻塞调用，成功返回 `True`；队列满时**不抛出 `asyncio.QueueFull`**，而是累加 `dropped_events`、在第 1 次及每 10 次拒收时记录警告日志，并返回 `False`。
- **总线状态异常**：总线未运行（`not _accepting`）或后台投递任务已取消/异常退出/意外结束时，`publish()` 会抛出 `RuntimeError` 并传给发布者。
- **分发与消费者异常隔离**：单个 `EventReceiver` 抛出异常时（例如某个 `AsyncConsumer` 的 `mailbox` 满导致 `receive` 抛出 `asyncio.QueueFull`），`EventDispatcher` 记录异常并继续向其余订阅者投递。异步处理器内部抛出的异常由 `AsyncConsumer.run()` 捕获并记录，处理失败的事件不重投。
- **排空与关闭语义**：`EventBus.stop(timeout: float = 5.0)` 具有幂等性（未运行直接返回，`timeout <= 0` 抛 `ValueError`）。调用后先停止接收新事件，再在超时时间内等待队列排空并监听投递任务是否异常退出（任务异常退出抛 `RuntimeError`，超时抛 `TimeoutError`），最后取消并回收排空任务与投递任务。`Runtime` 随后并发调用各 `AsyncConsumer.stop()`，等待各自 `mailbox.join()` 并取消消费者任务。

显示逻辑见 [`formatters/ui.py`](../src/lunia/formatters/ui.py)：名称未知时显示带 ID 的占位文本，媒体显示为 `[图片]`、`[语音]` 等标记，引用显示消息 ID；这些仅用于文本展示。
