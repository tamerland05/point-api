import asyncio
import logging
import traceback

from . import TipController

app_pooling = asyncio.Event()


async def start_pooling() -> None:
    while not app_pooling.is_set():
        await asyncio.sleep(5)
        try:
            await asyncio.gather(
                TipController.pooling_tips(),
            )
        except Exception as e:
            logging.exception(f"Pooling error: {e}\nTraceback: {traceback.format_exc()}")


def stop_pooling() -> None:
    app_pooling.set()
