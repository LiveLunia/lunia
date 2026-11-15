"""测试napcat连接"""

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

    task = asyncio.create_task(client.run())

    try:
        # 暂时等待连接建立
        await asyncio.sleep(2)

        result = await client.call_api("get_login_info", {})
        logger.info(f"API 响应: {result}")
        logger.warning("warning")
        logger.error("error")
        logger.critical("fatal")
        logger.debug("debug")

    finally:
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(main())
