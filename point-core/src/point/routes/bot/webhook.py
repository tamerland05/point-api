from fastapi import Request, APIRouter
from aiogram.types import Update

from point.controllers import PaymentController
from point.services import msb

router = APIRouter()


@router.post("")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.model_validate(data)

    if update.message and update.message.successful_payment:
        await PaymentController.process_payment(payload=update.message.successful_payment.invoice_payload)
    else:
        await msb.feed_update(update)

    return {"ok": True}
