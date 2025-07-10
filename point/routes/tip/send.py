from fastapi import APIRouter
from fastapi.params import Depends

from point.auth import get_user
from point.controllers import TipController
from point.view import AuthUser, CheckoutTipIn, TransactionOut

router = APIRouter()


@router.post("/checkout")
async def checkout_tip(checkout_in: CheckoutTipIn, user: AuthUser = Depends(get_user)) -> list[TransactionOut]:
    tip = await TipController.create_tip(
        checkout_in=checkout_in,
        sender_id=user.id,
    )
    return TransactionOut.list_validate(tip.transactions)
