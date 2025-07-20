from fastapi import Request, APIRouter
from aiogram.types import Update

from point.controllers import PaymentController
from point.services import bs

router = APIRouter()


@router.post("")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.model_validate(data)

    if update.pre_checkout_query is not None:
        await update.pre_checkout_query.answer(ok=True).as_(bs.bot)
    elif not (update.message is None or update.message.successful_payment is None):
        await PaymentController.process_payment(payload=update.message.successful_payment.invoice_payload)

    return {"ok": True}
