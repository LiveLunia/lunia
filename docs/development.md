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

## 检查与测试

```powershell
uv run ruff check .
uv run ruff format --check .
```

Ruff 的目标版本为 Python 3.13，行宽为 88，规则集见项目配置；检查排除了 `ref/`。

项目已声明 pytest 并配置导入模式和严格选项，但当前 `tests/` 只有手动联调脚本，没有按 pytest 默认规则收集的自动化测试用例。`uv run pytest` 当前可能以“未收集到测试”（退出码 5）结束，不能据此宣称测试通过。

### 手动联调入口

这些脚本依赖真实 NapCat，使用前应设置 `NAPCAT_TOKEN`；无需将账号或 Token 写入源码。

| 命令 | 用途与范围 |
| --- | --- |
| `uv run python -m tests.manual_napcat` | 连接后调用 `get_login_info`，输出 API 响应与各等级日志 |
| `uv run python -m tests.manual_napcat_events` | 持续接收事件，通过客户端调试日志查看解析结果 |
| `uv run python -m tests.manual_chat_ui` | 显示聊天事件文本；当前名称 Resolver 调用被注释，不等同于完整 Runtime |
| `uv run python -m tests.manual_napcat_cli` | 交互式调用 `NapCatAPI` 的公开异步方法，输入 `list`、`help` 或 `exit` 操作 |

API 控制台对内置只读集合之外的方法要求确认；API 封装包含发送消息、修改群资料等实际操作。接口是否可用取决于本机 NapCat、账号权限与参数，封装存在不表示已经逐项验证。

相关说明：[架构](architecture.md)、[事件](events.md)、[更新日志](../CHANGELOG.md)。
