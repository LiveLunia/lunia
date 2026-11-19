import asyncio
import logging
from unittest.mock import AsyncMock

import pytest

from lunia.adapters.napcat.adapter import NapCatAdapter
from lunia.core.runtime import Runtime


def test_napcat_events_reach_runtime_consumers(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setenv("NAPCAT_TOKEN", "test-token")
    caplog.set_level(logging.INFO, logger="lunia.core.runtime")

    async def scenario() -> None:
        runtime = Runtime()
        source = NapCatAdapter("secondary", runtime.bus, "ws://unused", "test-token")
        runtime.action_router.register(source.adapter_id, source.message_provider)

        send_message = AsyncMock()
        send_main_message = AsyncMock()
        send_poke = AsyncMock()
        monkeypatch.setattr(source.api.message, "send_msg", send_message)
        monkeypatch.setattr(runtime.adapter.api.message, "send_msg", send_main_message)
        monkeypatch.setattr(runtime.adapter.api.message, "send_poke", send_poke)
        monkeypatch.setattr(
            runtime.user_provider, "get_user_name", AsyncMock(return_value=None)
        )

        async def receive_events() -> None:
            common = {"self_id": 1, "user_id": 2, "group_id": 10, "time": 123}
            source.on_event(
                {
                    **common,
                    "post_type": "message",
                    "message_id": 42,
                    "message": [{"type": "text", "data": {"text": "Hello Lunia"}}],
                }
            )
            runtime.adapter.on_event(
                {
                    **common,
                    "post_type": "notice",
                    "notice_type": "notify",
                    "sub_type": "poke",
                    "target_id": 1,
                }
            )
            runtime.adapter.on_event(
                {
                    **common,
                    "post_type": "notice",
                    "notice_type": "group_recall",
                    "message_id": 42,
                    "operator_id": 2,
                }
            )

        monkeypatch.setattr(runtime.adapter.client, "run", receive_events)
        await asyncio.wait_for(runtime.run(), timeout=5)

        send_message.assert_awaited_once_with(
            message_type="group", group_id="10", message="检测到关键词"
        )
        send_main_message.assert_not_awaited()
        send_poke.assert_awaited_once_with(group_id="10", user_id="2")

    asyncio.run(scenario())

    messages = [
        record.getMessage()
        for record in caplog.records
        if record.name == "lunia.core.runtime"
    ]
    assert len(messages) == 3
    assert messages[0].endswith(": Hello Lunia")
    assert messages[1].endswith("戳了戳你")
    assert messages[2].endswith("撤回了一条消息")
