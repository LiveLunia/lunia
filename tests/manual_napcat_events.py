"""测试napcat事件"""

import asyncio
import os

from lunia.adapters.napcat.client import NapCatClient
from lunia.core.logging import get_logger, setup_logging

setup_logging()
logger = get_logger("lunia.test")


async def main() -> None:
    client = NapCatClient(
        url="ws://127.0.0.1:3799",
        token=os.environ["NAPCAT_TOKEN"],
    )

    await client.run()


if __name__ == "__main__":
    asyncio.run(main())
