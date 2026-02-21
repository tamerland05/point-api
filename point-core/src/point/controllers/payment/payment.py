import datetime
import logging
from uuid import UUID

from point.controllers.base import BaseController
from point.errors import ErrorCode
from point.models import Payment


class PaymentController(BaseController[Payment]):
    model = Payment
    error_code = ErrorCode.PAYMENT_NOT_FOUND

    PAYMENT_TTL = 60 * 60

    @classmethod
    async def process_payment(cls, payload: str) -> dict | None:
        try:
            payload = UUID(payload)
        except ValueError:
            logging.warning(f"Invalid payment UUID: {payload}")
            return {"ok": True}

        payment = await PaymentController.get_or_none(id=payload)
        if payment is None:
            logging.warning(f"Not fount payment with id: {payload}")
        elif payment.done:
            logging.warning(f"Already done payment with id: {payload}")
        else:
            payment.done = True
            await payment.save(update_fields=["done", "updated_at"])

        return None

    @classmethod
    async def clean_payments(cls) -> None:
        ttl_ago = datetime.datetime.now(datetime.UTC) - datetime.timedelta(seconds=cls.PAYMENT_TTL)
        await Payment.filter(updated_at__lt=ttl_ago, done=False).delete()
