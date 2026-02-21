import asyncio
import logging
import time

from point.controllers import (
    TipController,
    AssetController,
    EstablishmentRatingController,
    UserController,
    PaymentController,
)

MAX_LEGAL_DURATION = 3

app_pooling = asyncio.Event()


async def periodic_task(coro_func, interval: int):
    while not app_pooling.is_set():
        started_at = time.monotonic()
        try:
            await coro_func()

        except asyncio.CancelledError:
            logging.info("Pooling task %s cancelled", coro_func.__name__)
            raise

        except Exception:
            duration = time.monotonic() - started_at
            logging.exception(
                "Error in pooling task %s after %.3f sec",
                coro_func.__name__,
                duration,
            )

        else:
            duration = time.monotonic() - started_at
            if duration > MAX_LEGAL_DURATION:
                logging.info(
                    "Pooling task %s completed successfully in %.3f sec",
                    coro_func.__name__,
                    duration,
                )

        finally:
            await asyncio.sleep(interval)


async def start_pooling() -> None:
    await asyncio.gather(
        periodic_task(TipController.pooling_tips, 15),
        periodic_task(AssetController.update_prices, 30),
        periodic_task(EstablishmentRatingController.allow_ratings, 60),
        periodic_task(UserController.update_user_ranks, 60),
        periodic_task(PaymentController.clean_payments, PaymentController.PAYMENT_TTL)
    )


def stop_pooling() -> None:
    app_pooling.set()
