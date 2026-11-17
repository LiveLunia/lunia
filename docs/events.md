# 事件说明

内部事件定义见 [`core/events.py`](../src/lunia/core/events.py)，QQ 转换逻辑见 [`adapters/napcat/parser.py`](../src/lunia/adapters/napcat/parser.py)。这些 `TypedDict` 是类型约定，不是完整的运行时输入校验器。

## 公共字段

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
2. `echo` 不为 `None` 的数据作为 API 响应处理，不送入聊天解析器。
3. 其余数据通过同步回调交给 `NapCatAdapter.on_event`，由 Adapter 调用 `parse_chat`。解析异常会记录并跳过；不支持的上报（包括心跳和其他通知）返回 `None`，不投递聊天事件。
4. Adapter 按 `event["kind"]` 直接调用 `EventDispatcher.dispatch`，不等待消费者或平台查询。
5. 分发器将同一个事件对象交给各订阅者，并发执行其异步处理器。

Resolver 不在上述必经路径中。消费者需要显示名称时自行调用 Resolver，使用返回的事件副本；当前关键词回复与回戳不等待名称补全。处理器应避免修改共享的原始事件，防止影响其他消费者。

Client 的 `on_event` 回调接收原始上报字典并同步返回；标准化后的 `ChatEvent` 只交给 Dispatcher 的异步消费者。API 响应不会进入 Adapter 或 Parser。

分发器不等待处理器执行完成，不提供串行顺序、事件持久化或失败重投。处理异常由分发器记录；没有订阅者时不会创建任务。

显示逻辑见 [`formatters/ui.py`](../src/lunia/formatters/ui.py)：名称未知时显示带 ID 的占位文本，媒体显示为 `[图片]`、`[语音]` 等标记，引用显示消息 ID；这些仅用于文本展示。
