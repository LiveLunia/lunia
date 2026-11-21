# 开发指南

## 环境与命令

在项目根目录使用 Python 3.13 和 uv。版本与依赖约束以 [pyproject.toml](../pyproject.toml)、[uv.lock](../uv.lock) 和 [.python-version](../.python-version) 为准。运行依赖包含 `websockets` 与 `openai`，开发依赖包含 `pytest` 与 `ruff`。

在普通本机 PowerShell 中安装锁定依赖并验证入口：

```powershell
uv sync --locked
uv run python --version
uv run lunia
```

`uv sync` 默认包含 `dev` 依赖组。`uv run lunia` 和 `uv run python -m lunia` 均调用初始化入口，只输出提示并退出；聊天演示需使用独立入口：

```powershell
uv run python -m lunia.core.runtime
```

启动 `lunia.core.runtime` 需要先启动已登录的 NapCat、启用 WebSocket 服务（消息段数组上报格式），并在当前终端设置 `NAPCAT_TOKEN`、`DEEPSEEK_API_KEY` 与 `TEST_QQ`。环境变量输入示例见 [README 快速开始](../README.md#环境要求与快速开始)。

## 当前配置行为

| 配置或入口 | 实际行为 |
| --- | --- |
| `NAPCAT_TOKEN` | `Runtime.__init__()` 与手动 NapCat 脚本从进程环境读取；缺失时抛出 `KeyError` |
| `DEEPSEEK_API_KEY` | `Runtime.__init__()` 创建 `LLMManager` 时从进程环境读取；缺失时抛出 `KeyError` |
| `TEST_QQ` | `demo/chat.py` 在**模块导入阶段**直接读取（用于私聊白名单过滤）；未设置时导入 `lunia.core.runtime` 或 `lunia.demo.chat` 就会抛出 `KeyError` |
| Runtime 的 WebSocket 地址 | 固定为 `ws://127.0.0.1:3799`，没有读取 `NAPCAT_URL` |
| Runtime 的 LLM 配置 | 固定注册 `deepseek` Provider（`https://api.deepseek.com`）与 `chat` 模型别名（当前代码写为 `model_id="deepseek-flash"`） |
| `tests.manual_napcat_cli` 的 `NAPCAT_URL` | 可从进程环境覆盖，缺省为 `ws://127.0.0.1:3799` |
| 其他手动联调脚本的地址 | 固定为 `ws://127.0.0.1:3799`（仅依赖 `NAPCAT_TOKEN`，不依赖 LLM 环境变量） |
| `.env` / `.env.example` | 程序没有自动加载逻辑；示例文件暂未定义配置项 |
| VS Code 终端 | 仓库配置启用了 `python.terminal.useEnvFile`，编辑器行为不能替代普通终端的环境设置 |

运行 `lunia.core.runtime` 时：
- 所有聊天事件经 `on_chat_ui` 补全名称后输出终端与文件日志。
- `ChatDemo` 对群聊中包含 `lunia`（不区分大小写）的文本消息，以及私聊中来自 `TEST_QQ` 的文本消息，发起单轮 LLM 补全并经 `ActionRouter` 回复。
- 被其他用户戳一戳时，由 `on_poke` 直接调用 NapCat API 回戳。

按 `Ctrl+C` 停止。当前没有配置文件加载、数据库配置或部署服务配置。

## API 调用组织

`NapCatAPI` 通过按功能领域组织的组合对象提供 108 个 API 方法：

```python
from lunia.adapters.napcat.api import NapCatAPI

api = NapCatAPI(client)  # 复用已有的 NapCatClient。
await api.message.send_group_msg(group_id="测试群 ID", message="你好")
await api.group.get_group_member_info(group_id="测试群 ID", user_id="测试用户 ID")
await api.user.get_stranger_info(user_id="测试用户 ID")
```

所有调用方统一使用分类对象，不再提供扁平方法代理。方法签名、默认值、说明文档和请求行为保持不变，各分类对象共享传入的 Client，不创建独立连接。底层仍可通过 `client.call_api(action, params)` 调用协议端接口。

| 分类 | 已封装方法数 | 范围 |
| --- | ---: | --- |
| `message` | 17 | 消息发送、读取、历史、转发、已读与戳一戳 |
| `group` | 50 | 群资料、管理、相册、群待办及群组扩展 |
| `user` | 16 | 用户资料、好友、备注、点赞与用户扩展 |
| `file` | 14 | 文件和媒体信息、上传下载及群文件管理 |
| `system` | 9 | 系统信息、能力检查、状态及链接安全检查 |
| `extensions` | 2 | `ocr_image` 与跨领域的 `handle_quick_operation` |

分类主要参考已连接的 [NapCat Apifox](https://napcat.apifox.cn) 4.15.1 文档。Go-CQHTTP 兼容接口按实际功能归类，不单设兼容接口集合；笼统的“扩展接口”也按用途归类，OCR 与跨领域快速操作放入 `extensions`。分类不表示 OneBot 11 标准归属，也不表示已完成实机兼容性验证。

NapCat 长期作为独立 Adapter 保留，允许继续使用这些混合能力。流式、频道、AI、QQ 空间等尚未封装的类别暂不创建空模块；将来有具体需求时再添加。其他平台的 Adapter 仍是后续规划。

当前封装中的参数别名、字符串兼容值、历史消息的两种排序字段、服务端与客户端超时分别保留。服务器版本支持范围及这些字段的实际语义仍需另行核实。

## 检查与测试

```powershell
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

Ruff 的目标版本为 Python 3.13，行宽为 88，规则集见项目配置；检查排除了 `ref/`。

当前仓库包含以下离线自动化测试文件（使用内存替身 / Mock，不依赖真实网络）：

- `tests/test_event_bus.py`：验证总线 FIFO 投递、满队拒收返回 `False` 与 `dropped_events` 计数、投递任务异常退出检测、幂等停止及关闭超时。
- `tests/test_action_router.py`：验证 `ActionRouter` 按 `adapter_id` 将 `SendMessage` 路由至目标 `MessageProvider`。
- `tests/test_llm_manager.py`：验证 `LLMManager` 按模型别名路由至对应客户端，替换底层客户端避免真实 HTTP 请求。
- `tests/test_napcat_api.py`：验证 108 个 API 方法的分类与共享 Client 路由，以及请求参数、超时、返回值、参数校验和控制台交互。
- `tests/test_runtime.py`：端到端验证 `NapCatAdapter`、`EventBus`、`ActionRouter` 与 `Runtime` 消费者流程。**注意**：当前该测试仍对应旧版固定关键词回复（`"检测到关键词"`），且受 `demo/chat.py` 导入期读取 `TEST_QQ` 及 `Runtime` 新增 `DEEPSEEK_API_KEY` 影响，尚未同步更新至 `ChatDemo` / `LLMManager` 版本。

### 手动联调入口

这些脚本依赖真实 NapCat，使用前应设置 `NAPCAT_TOKEN`；无需将账号或 Token 写入源码。

| 命令 | 用途与范围 |
| --- | --- |
| `uv run python -m tests.manual_napcat` | 连接后调用 `get_login_info`，输出 API 响应与各等级日志 |
| `uv run python -m tests.manual_napcat_events` | 通过 `NapCatAdapter` 与 `EventBus` 持续接收并发布 `EventEnvelope`，在调试日志查看解析结果 |
| `uv run python -m tests.manual_chat_ui` | 通过 `NapCatAdapter`、`EventBus` 和同步订阅回调显示原始聊天事件文本 |
| `uv run python -m tests.manual_napcat_cli` | 交互式调用 `NapCatAPI` 的公开异步方法，输入 `list`、`help` 或 `exit` 操作 |

API 控制台使用 `分类.方法名`，例如 `message.get_msg`、`group.get_group_info`、`user.get_stranger_info`；`list` 列出可调用的方法。

API 控制台对内置只读集合之外的方法要求确认；API 封装包含发送消息、修改群资料等实际操作。接口是否可用取决于本机 NapCat、账号权限与参数，封装存在不表示已经逐项验证。

相关说明：[架构](architecture.md)、[事件](events.md)、[更新日志](../CHANGELOG.md)。
