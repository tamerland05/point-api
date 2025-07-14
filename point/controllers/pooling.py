import asyncio
import logging

from point.controllers import TipController, AssetController

app_pooling = asyncio.Event()


async def start_pooling() -> None:
    while not app_pooling.is_set():
        try:
            await asyncio.gather(
                TipController.pooling_tips(),
                AssetController.update_prices()
            )
        except Exception as e:
            logging.exception(f"Pooling error: {e}")
        await asyncio.sleep(15)


def stop_pooling() -> None:
    app_pooling.set()
