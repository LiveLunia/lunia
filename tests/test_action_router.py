import asyncio

from lunia.core.actions.models import SendMessage
from lunia.core.actions.router import ActionRouter


def test_action_router_routes_by_adapter_id() -> None:
    class FakeProvider:
        def __init__(self) -> None:
            self.messages = []

        async def send_message(
            self,
            conversation_type,
            conversation_id,
            content,
        ):
            self.messages.append((conversation_type, conversation_id, content))
            return {"status": "ok"}

    async def scenario() -> None:
        router = ActionRouter()

        main = FakeProvider()
        test = FakeProvider()

        router.register("napcat-main", main)
        router.register("napcat-test", test)

        await router.execute(
            SendMessage(
                adapter_id="napcat-test",
                conversation_type="group",
                conversation_id="123456",
                content="你好",
            )
        )

        assert main.messages == []
        assert test.messages == [("group", "123456", "你好")]

    asyncio.run(scenario())
