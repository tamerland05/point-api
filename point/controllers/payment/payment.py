import logging
from uuid import UUID

from point.controllers.base import BaseController
from point.errors import ErrorCode
from point.models import Payment


class PaymentController(BaseController[Payment]):
    model = Payment
    error_code = ErrorCode.PAYMENT_NOT_FOUND

    @classmethod
    async def process_payment(cls, payload: str):
        try:
            payload = UUID(payload)
        except ValueError:
            logging.warn(f"Invalid payment UUID: {payload}")
            return {"ok": True}

        payment = await PaymentController.get_or_none(id=payload)
        if payment is None:
            logging.warn(f"Not fount payment with id: {payload}")
        elif payment.done:
            logging.warn(f"Already done payment with id: {payload}")
        else:
            payment.done = True
            await payment.save(update_fields=["done", "updated_at"])

        return None
