import asyncio
import inspect
import json
import os
from typing import Any

from lunia.adapters.napcat.api import NapCatAPI
from lunia.adapters.napcat.client import NapCatClient
from lunia.core.logging import setup_logging

# 默认允许直接执行的只读接口；其余接口需要确认
READ_ONLY = {
    "system.get_login_info",
    "system.get_status",
    "system.get_version_info",
    "message.get_msg",
    "group.get_group_info",
    "group.get_group_list",
    "group.get_group_member_info",
    "group.get_group_member_list",
    "user.get_friend_list",
    "user.get_stranger_info",
}


async def ask(prompt: str) -> str:
    """异步读取终端输入。"""
    return await asyncio.to_thread(input, prompt)


def parse_value(raw: str) -> Any:
    """解析用户输入，支持普通文本和 JSON 值。"""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def get_methods(api: NapCatAPI) -> dict[str, Any]:
    """以“分类.方法名”列出各领域公开的异步方法。"""
    return {
        f"{domain}.{name}": member
        for domain in ("message", "group", "user", "file", "system", "extensions")
        for name, member in inspect.getmembers(getattr(api, domain))
        if not name.startswith("_") and inspect.iscoroutinefunction(member)
    }


async def execute(api: NapCatAPI, name: str) -> None:
    """收集 API 参数，确认后执行。"""
    domain, method_name = name.split(".", 1)
    method = getattr(getattr(api, domain), method_name)
    signature = inspect.signature(method)
    kwargs: dict[str, Any] = {}

    print(f"\nAPI: {name}")
    if method.__doc__:
        print(inspect.cleandoc(method.__doc__).splitlines()[0])

    for param in signature.parameters.values():
        if param.name == "self":
            continue

        optional = param.default is not inspect.Parameter.empty
        suffix = " (可选，回车跳过)" if optional else ""
        raw = (await ask(f"  {param.name}{suffix}: ")).strip()

        if not raw and optional:
            continue
        if not raw:
            print(f"缺少必填参数：{param.name}")
            return

        kwargs[param.name] = parse_value(raw)

    print("\n请求参数：")
    print(json.dumps(kwargs, ensure_ascii=False, indent=2, default=str))

    if name not in READ_ONLY:
        answer = (await ask("此操作可能产生副作用，确认执行？[y/N] ")).lower()
        if answer != "y":
            print("已取消")
            return

    try:
        result = await method(**kwargs)
        print("\nAPI 响应：")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as exc:
        print(f"调用失败：{type(exc).__name__}: {exc}")


async def wait_connected(client: NapCatClient) -> None:
    """等待客户端首次连接成功。"""
    async with asyncio.timeout(10):
        while client.ws is None:
            await asyncio.sleep(0.1)


async def main() -> None:
    setup_logging()

    client = NapCatClient(
        url=os.getenv("NAPCAT_URL", "ws://127.0.0.1:3799"),
        token=os.environ["NAPCAT_TOKEN"],
    )
    api = NapCatAPI(client)
    methods = get_methods(api)

    task = asyncio.create_task(client.run())

    try:
        try:
            await wait_connected(client)
        except TimeoutError:
            print("NapCat 连接超时，请检查服务是否启动及端口配置。")
            return
        print(f"\nLunia API Console · {len(methods)} methods")
        print("输入 list 查看接口，help 查看帮助，exit 退出。")

        while True:
            command = (await ask("\nnapcat > ")).strip()

            if command in {"exit", "quit"}:
                break
            if command == "help":
                print("list: 列出 API | 输入 分类.方法名 调用 | exit: 退出")
                continue
            if command == "list":
                print("\n".join(sorted(methods)))
                continue
            if command not in methods:
                print("未知 API，请输入 list 查看支持的接口。")
                continue

            await execute(api, command)

    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(main())
