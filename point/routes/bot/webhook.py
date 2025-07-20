import logging
from uuid import UUID

from fastapi import Request, APIRouter
from aiogram.types import Update

from point.controllers import PaymentController

router = APIRouter()


@router.post("")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.model_validate(data)

    if update.pre_checkout_query is not None:
        await update.pre_checkout_query.answer(ok=True)
        return {"ok": True}

    if update.message is None or update.message.successful_payment is None:
        return {"ok": True}

    payload = update.message.successful_payment.invoice_payload
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

    return {"ok": True}
