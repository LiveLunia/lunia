import asyncio
import json
import logging
from contextlib import asynccontextmanager
from copy import deepcopy
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from lunia.adapters.napcat.adapter import NapCatAdapter
from lunia.adapters.napcat.client import NapCatClient
from lunia.core.dispatcher import EventDispatcher
from lunia.core.events import ChatEvent
from lunia.core.runtime import Runtime


class FakeWebSocket:
    def __init__(self) -> None:
        self.incoming: asyncio.Queue[str | None] = asyncio.Queue()
        self.requests: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

    async def send(self, message: str) -> None:
        self.requests.put_nowait(json.loads(message))

    def __aiter__(self):
        return self

    async def __anext__(self) -> str:
        message = await self.incoming.get()
        if message is None:
            raise StopAsyncIteration
        return message

    def feed(self, data: Any) -> None:
        self.incoming.put_nowait(json.dumps(data))

    def respond(self, request: dict[str, Any], data: Any) -> dict[str, Any]:
        response = {"echo": request["echo"], "status": "ok", "retcode": 0, "data": data}
        self.feed(response)
        return response


@asynccontextmanager
async def receiving(client: NapCatClient, socket: FakeWebSocket):
    with patch.object(client, "ws", socket):
        receiver = asyncio.create_task(client._receive_loop())
        try:
            async with asyncio.timeout(2):
                yield
        finally:
            socket.incoming.put_nowait(None)
            try:
                await asyncio.wait_for(receiver, 2)
            finally:
                client._fail_pending()


def make_report(*, group: bool = False, actor_id: int = 2) -> dict[str, Any]:
    report: dict[str, Any] = {
        "post_type": "message",
        "self_id": 1,
        "time": 1700000000,
        "user_id": actor_id,
        "message_id": 3,
        "sender": {"nickname": "昵称", "card": "群名片", "remark": "私聊备注"},
        "message": [{"type": "text", "data": {"text": "LuNiA"}}],
    }
    if group:
        report.update(group_id=10, group_name="测试群")
    return report


def test_client_delivers_raw_reports_and_matches_out_of_order_responses():
    async def scenario():
        reports = []
        client = NapCatClient("ws://unused", "unused", on_event=reports.append)
        socket = FakeWebSocket()
        raw = {"post_type": "custom", "echo": None, "data": {"value": 1}}

        async with receiving(client, socket):
            first = asyncio.create_task(client.call_api("first", {}))
            second = asyncio.create_task(client.call_api("second", {}))
            requests = [await socket.requests.get(), await socket.requests.get()]
            socket.feed(raw)
            socket.feed({"echo": "unknown", "status": "ok"})
            second_response = socket.respond(requests[1], {"value": 2})
            first_response = socket.respond(requests[0], {"value": 1})
            assert await second == second_response
            assert await first == first_response
            socket.feed(first_response)  # 迟到或重复的响应也不能变成事件。

        assert reports == [raw]
        assert client.pending == {}

    asyncio.run(scenario())


@pytest.mark.parametrize("group", [False, True], ids=["private", "group"])
@pytest.mark.parametrize("kind", ["message", "poke", "recall"])
def test_adapter_preserves_chat_events(group, kind):
    async def scenario():
        dispatcher = EventDispatcher()
        adapter = NapCatAdapter(dispatcher)
        events = []

        async def collect(event: ChatEvent):
            events.append(event)

        raw = make_report(group=group)
        if kind == "message":
            raw["message"].append({"type": "future", "data": {"nested": [1, 2]}})
            payload = {
                "message_id": "3",
                "segments": [
                    {"type": "text", "text": "LuNiA"},
                    {
                        "type": "unknown",
                        "original_type": "future",
                        "data": {"nested": [1, 2]},
                    },
                ],
            }
        elif kind == "poke":
            raw.update(
                post_type="notice",
                notice_type="notify",
                sub_type="poke",
                target_id=1,
                raw_info=[
                    {"type": "nor", "txt": "轻轻戳了戳"},
                    {"type": "nor", "txt": "的肩膀"},
                ],
            )
            payload = {
                "target_id": "1",
                "target_name": None,
                "target_alias": None,
                "action_text": "轻轻戳了戳",
                "suffix_text": "的肩膀",
            }
        else:
            raw.update(
                post_type="notice",
                notice_type="group_recall" if group else "friend_recall",
                operator_id=4,
            )
            payload = {
                "message_id": "3",
                "sender_id": "2",
                "sender_name": None,
                "sender_alias": None,
            }

        original = deepcopy(raw)
        expected = {
            "kind": f"chat.{kind}",
            "platform": "qq",
            "account_id": "1",
            "conversation_type": "group" if group else "private",
            "conversation_id": "10" if group else "2",
            "conversation_name": "测试群" if group else None,
            "actor_id": "4" if group and kind == "recall" else "2",
            "actor_name": "昵称" if kind == "message" else None,
            "actor_alias": ("群名片" if group else "私聊备注")
            if kind == "message"
            else None,
            "timestamp": 1700000000,
            "payload": payload,
        }
        dispatcher.subscribe(expected["kind"], collect)
        adapter.on_event(raw)
        await dispatcher.shutdown()
        assert events == [expected]
        assert raw == original

    asyncio.run(scenario())


@pytest.mark.parametrize(
    "invalid_report",
    [
        {"post_type": "message"},
        {**make_report(), "message": "unsupported string format"},
        {**make_report(), "sender": ["invalid sender"]},
        {
            **make_report(),
            "post_type": "notice",
            "notice_type": "notify",
            "sub_type": "poke",
            "target_id": 1,
            "raw_info": 1,
        },
    ],
    ids=["missing-fields", "invalid-segments", "invalid-sender", "invalid-poke"],
)
def test_parse_failure_is_logged_and_receiving_continues(invalid_report, caplog):
    async def scenario():
        dispatcher = EventDispatcher()
        adapter = NapCatAdapter(dispatcher)
        client = NapCatClient("ws://unused", "unused", on_event=adapter.on_event)
        socket = FakeWebSocket()
        events = []

        async def collect(event: ChatEvent):
            events.append(event)

        dispatcher.subscribe("chat.message", collect)
        async with receiving(client, socket):
            socket.incoming.put_nowait("not JSON")
            socket.feed(["not an event object"])
            socket.feed(invalid_report)
            socket.feed({"post_type": "meta_event", "meta_event_type": "heartbeat"})
            socket.feed(make_report())
        await dispatcher.shutdown()
        assert len(events) == 1
        assert events[0]["kind"] == "chat.message"

    with caplog.at_level(logging.ERROR, logger="lunia.adapters.napcat.adapter"):
        asyncio.run(scenario())
    errors = [r for r in caplog.records if r.name == "lunia.adapters.napcat.adapter"]
    assert len(errors) == 1
    assert "上报解析失败" in errors[0].message
    assert errors[0].exc_info is not None


def test_adapter_does_not_hide_dispatch_errors(monkeypatch):
    dispatcher = EventDispatcher()
    adapter = NapCatAdapter(dispatcher)

    def fail_dispatch(kind, event):
        raise RuntimeError("dispatcher unavailable")

    monkeypatch.setattr(dispatcher, "dispatch", fail_dispatch)
    with pytest.raises(RuntimeError, match="dispatcher unavailable"):
        adapter.on_event(make_report())


def test_runtime_name_query_does_not_block_responses_and_preserves_remark(
    monkeypatch, caplog
):
    monkeypatch.setenv("NAPCAT_TOKEN", "offline-test-token")

    async def scenario():
        runtime = Runtime()
        socket = FakeWebSocket()
        raw = make_report()
        raw["sender"] = {}
        raw["message"] = [{"type": "text", "data": {"text": "你好"}}]

        try:
            async with receiving(runtime.client, socket):
                socket.feed(raw)
                query = await socket.requests.get()
                assert query["action"] == "get_stranger_info"
                assert query["params"]["user_id"] == "2"

                # 名称查询仍在等待时，另一请求必须能完成响应匹配。
                status_task = asyncio.create_task(runtime.api.system.get_status())
                status_request = await socket.requests.get()
                assert status_request["action"] == "get_status"
                expected = socket.respond(status_request, {"online": True})
                assert await status_task == expected
                assert query["echo"] in runtime.client.pending

                socket.respond(query, {"nickname": "查询昵称", "remark": "兼容备注"})
                await runtime.dispatcher.shutdown()

            key = ("qq", "1", "private", "2", "2")
            assert runtime.user_cache.get(key) == {
                "nickname": "查询昵称",
                "alias": "兼容备注",
            }
            assert runtime.client.pending == {}
        finally:
            await runtime.dispatcher.shutdown(timeout=0)

    with caplog.at_level(logging.INFO, logger="lunia.core.runtime"):
        asyncio.run(scenario())
    assert "[私聊] <- (查询昵称)兼容备注: 你好" in caplog.text


@pytest.mark.parametrize(
    ("group", "kind", "actor_id", "target_id", "text", "method", "params"),
    [
        (
            False,
            "message",
            2,
            1,
            "LuNiA",
            "send_private_msg",
            {"user_id": "2", "message": "检测到关键词"},
        ),
        (
            True,
            "message",
            2,
            1,
            "lunia",
            "send_group_msg",
            {"group_id": "10", "message": "检测到关键词"},
        ),
        (False, "message", 2, 1, "hello", None, None),
        (False, "message", 1, 1, "lunia", None, None),
        (False, "poke", 2, 1, "", "send_poke", {"user_id": "2"}),
        (True, "poke", 2, 1, "", "send_poke", {"group_id": "10", "user_id": "2"}),
        (False, "poke", 2, 3, "", None, None),
        (False, "poke", 1, 1, "", None, None),
    ],
    ids=[
        "private-keyword",
        "group-keyword",
        "no-keyword",
        "own-message",
        "private-poke",
        "group-poke",
        "poke-someone-else",
        "own-poke",
    ],
)
def test_runtime_preserves_demo_behaviors(
    monkeypatch, group, kind, actor_id, target_id, text, method, params
):
    monkeypatch.setenv("NAPCAT_TOKEN", "offline-test-token")

    async def scenario():
        runtime = Runtime()
        sends = {}
        for name in ("send_private_msg", "send_group_msg", "send_poke"):
            sends[name] = AsyncMock()
            monkeypatch.setattr(runtime.api.message, name, sends[name])
        group_query = AsyncMock()
        private_query = AsyncMock()
        monkeypatch.setattr(runtime.api.group, "get_group_member_info", group_query)
        monkeypatch.setattr(runtime.api.user, "get_stranger_info", private_query)
        key = (
            "qq",
            "1",
            "group" if group else "private",
            "10" if group else str(actor_id),
            str(actor_id),
        )
        runtime.user_cache.update(key, nickname="缓存昵称", alias="缓存别名")
        raw = make_report(group=group, actor_id=actor_id)
        raw["message"] = [{"type": "text", "data": {"text": text}}]
        if kind == "poke":
            raw.update(
                post_type="notice",
                notice_type="notify",
                sub_type="poke",
                target_id=target_id,
            )

        runtime.adapter.on_event(raw)
        await runtime.dispatcher.shutdown()

        for name, send in sends.items():
            if name == method:
                send.assert_awaited_once_with(**params)
            else:
                send.assert_not_awaited()
        group_query.assert_not_awaited()
        private_query.assert_not_awaited()
        if group:
            assert runtime.conver_cache.get(("qq", "1", "group", "10")) == "测试群"

    asyncio.run(scenario())


def test_request_timeout_and_disconnect_clean_pending():
    async def scenario():
        client = NapCatClient("ws://unused", "unused")
        socket = FakeWebSocket()
        with patch.object(client, "ws", socket):
            with pytest.raises(TimeoutError):
                await client.call_api("timeout", {}, timeout=0)
            assert client.pending == {}
            await socket.requests.get()

            request = asyncio.create_task(
                client.call_api("disconnect", {}, timeout=None)
            )
            await asyncio.wait_for(socket.requests.get(), 2)
            client._fail_pending()
            with pytest.raises(ConnectionError, match="NapCat 连接中断"):
                await asyncio.wait_for(request, 2)
            assert client.pending == {}

    asyncio.run(scenario())
