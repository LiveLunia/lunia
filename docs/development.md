# 开发指南

## 环境与命令

在项目根目录使用 Python 3.13 和 uv。版本与依赖约束以 [pyproject.toml](../pyproject.toml)、[uv.lock](../uv.lock) 和 [.python-version](../.python-version) 为准。

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

聊天演示需要先启动已登录的 NapCat、启用 WebSocket 服务、设置当前终端的 `NAPCAT_TOKEN`，并使用消息段数组上报格式。Token 输入示例见 [README 快速开始](../README.md#环境要求与快速开始)。

## 当前配置行为

| 配置或入口 | 实际行为 |
| --- | --- |
| `NAPCAT_TOKEN` | Runtime 与手动 NapCat 脚本从进程环境读取；缺失时会抛出 `KeyError` |
| Runtime 的 WebSocket 地址 | 固定为 `ws://127.0.0.1:3799`，没有读取 `NAPCAT_URL` |
| `tests.manual_napcat_cli` 的 `NAPCAT_URL` | 可从进程环境覆盖，缺省为上述本机地址 |
| 其他手动联调脚本的地址 | 固定为上述本机地址 |
| `.env` / `.env.example` | 程序没有自动加载逻辑；示例文件暂未定义配置项 |
| VS Code 终端 | 仓库配置启用了 `python.terminal.useEnvFile`，编辑器行为不能替代普通终端的环境设置 |

运行演示时，消息中包含 `lunia` 会触发固定回复，被其他用户戳一戳会触发回戳。按 `Ctrl+C` 结束。当前没有模型配置、数据库配置或部署服务配置。

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

当前封装中的参数别名、字符串兼容值、历史消息的两种排序字段、服务端与客户端超时分别保留。服务器版本支持范围及这些字段的实际语义仍需另行核实，不在本次代码组织调整中标准化。

## 检查与测试

```powershell
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

Ruff 的目标版本为 Python 3.13，行宽为 88，规则集见项目配置；检查排除了 `ref/`。

自动化测试可离线运行，使用内存 WebSocket 替身和测试 Token。

- `tests/test_event_bus.py` 验证总线按入队顺序投递，并在停止时排空队列。
- `tests/test_napcat_adapter.py` 验证上报与 API 响应分流、解析失败隔离、同连接上的并发查询、名称补全、演示行为及 Runtime 启停。
- `tests/test_napcat_api.py` 验证 108 个 API 方法的分类与共享 Client 路由，以及请求参数、超时、返回值、参数校验和控制台交互。

### 手动联调入口

这些脚本依赖真实 NapCat，使用前应设置 `NAPCAT_TOKEN`；无需将账号或 Token 写入源码。

| 命令 | 用途与范围 |
| --- | --- |
| `uv run python -m tests.manual_napcat` | 连接后调用 `get_login_info`，输出 API 响应与各等级日志 |
| `uv run python -m tests.manual_napcat_events` | 持续接收并发布事件，通过 Adapter 调试日志查看解析结果 |
| `uv run python -m tests.manual_chat_ui` | 通过总线和同步订阅回调显示原始聊天事件文本 |
| `uv run python -m tests.manual_napcat_cli` | 交互式调用 `NapCatAPI` 的公开异步方法，输入 `list`、`help` 或 `exit` 操作 |

API 控制台使用 `分类.方法名`，例如 `message.get_msg`、`group.get_group_info`、`user.get_stranger_info`；`list` 列出可调用的方法。

API 控制台对内置只读集合之外的方法要求确认；API 封装包含发送消息、修改群资料等实际操作。接口是否可用取决于本机 NapCat、账号权限与参数，封装存在不表示已经逐项验证。

相关说明：[架构](architecture.md)、[事件](events.md)、[更新日志](../CHANGELOG.md)。
