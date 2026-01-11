from fastapi import Request, APIRouter
from aiogram.types import Update

from point.controllers import PaymentController
from point.services import bs

router = APIRouter()


@router.post("")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.model_validate(data)

    if update.message and update.message.successful_payment:
        await PaymentController.process_payment(payload=update.message.successful_payment.invoice_payload)
    else:
        await bs.feed_update(update)

    return {"ok": True}
