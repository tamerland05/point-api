import asyncio

from fastapi import APIRouter, Depends

from point.auth import get_user
from point.config import settings
from point.controllers import EstablishmentController, UserController, PaymentController
from point_shared.entity_types import PaymentTagType
from point.i18 import translate
from point.models.utils import hash_to_link
from point.services import msb
from point.view import AuthUser, EstablishmentRatingDbCreateIn, EstablishmentRatingCreateIn, StarsInvoiceRequest

router = APIRouter()


@router.post("/create-invoice")
async def set_establishment_rating(
        establishment_rating_in: EstablishmentRatingCreateIn,
        user: AuthUser = Depends(get_user)
) -> str:
    user, _ = await asyncio.gather(
        UserController.get_user(user_id=user.id),
        EstablishmentController.get(id=establishment_rating_in.establishment_id, enabled=True),
    )
    establishment_in = EstablishmentRatingDbCreateIn(
        user_id=user.id,
        **establishment_rating_in.model_dump(mode="json"),
    )
    payment = await PaymentController.model.create(
        user_id=user.id,
        tag=PaymentTagType.stars_establishment_rating,
        meta=establishment_in.model_dump(mode="json"),
    )

    domain = "payment." + PaymentTagType.stars_establishment_rating
    return await msb.create_invoice_link(
        request=StarsInvoiceRequest(
            payload=str(payment.id),
            title=translate("title", domain=domain),
            description=translate("description", domain=domain),
            amount=settings.set_rating_amount,
            lang=user.language_code,
            photo_url=hash_to_link(settings.logo_hash)
        )
    )
