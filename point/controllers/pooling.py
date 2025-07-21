import asyncio
import logging

from point.controllers import TipController, AssetController, EstablishmentRatingController, UserController

app_pooling = asyncio.Event()


async def periodic_task(coro_func, interval: int):
    while not app_pooling.is_set():
        try:
            await asyncio.gather(coro_func(), asyncio.sleep(interval))
        except Exception as e:
            logging.exception(f"Error in pooling task {coro_func.__name__}: {e}")


async def start_pooling() -> None:
    await asyncio.gather(
        periodic_task(TipController.pooling_tips, 15),
        periodic_task(AssetController.update_prices, 30),
        periodic_task(EstablishmentRatingController.allow_ratings, 60),
        periodic_task(UserController.update_user_ranks, 60),
    )


def stop_pooling() -> None:
    app_pooling.set()
