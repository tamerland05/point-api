import asyncio
from collections import defaultdict
from uuid import UUID

from pydantic import ValidationError
from tortoise.expressions import F
from tortoise.transactions import in_transaction

from point.config import settings
from point.controllers.base import BaseController
from point_shared.entity_types import PaymentTagType
from point.errors import ErrorCode
from point.models import EstablishmentRating, Payment, Establishment, User
from point.view import EstablishmentRatingDbCreateIn


class EstablishmentRatingController(BaseController[EstablishmentRating]):
    model = EstablishmentRating
    error_code = ErrorCode.ESTABLISHMENT_RATING_NOT_FOUND

    @classmethod
    async def allow_ratings(cls) -> None:
        rating_payments = await Payment.filter(done=True, tag=PaymentTagType.stars_establishment_rating)
        if len(rating_payments) == 0:
            return

        establishment_ratings = []
        establishments = defaultdict(lambda: [0, 0])
        for rp in rating_payments:
            try:
                rating = EstablishmentRatingDbCreateIn.model_validate(rp.meta)
            except ValidationError:
                continue

            establishment_ratings.append(cls.model(**rp.meta))
            establishments[rating.establishment_id][0] += 1
            establishments[rating.establishment_id][1] += rating.mark

        async with (in_transaction()):
            await cls.model.bulk_create(establishment_ratings)
            await cls.update_establishments(establishments_rates=establishments)
            await User.filter(
                id__in=set(payment.user_id for payment in rating_payments),
            ).select_for_update(no_key=True).update(
                tasks_bonus_balance=F("tasks_bonus_balance") + settings.bonus_reward_for_rating
            )
            await Payment.filter(id__in=[rp.id for rp in rating_payments]).delete()

    @classmethod
    async def update_establishments(cls, establishments_rates: dict) -> None:
        establishments = await Establishment.filter(
            id__in=establishments_rates.keys()
        ).select_for_update(no_key=True)

        update_tasks = []
        for e in establishments:
            e.rating_count += establishments_rates[e.id][0]
            e.rating_sum += establishments_rates[e.id][1]
            update_tasks.append(e.save(update_fields=['rating_count', 'rating_sum']))

        await asyncio.gather(*update_tasks)

    @classmethod
    async def get_user_rating(cls, establishment_id: UUID, user_id) -> int | None:
        ratings = await (
            cls.filter(establishment_id=establishment_id, user_id=user_id)
            .order_by("-created_at")
            .limit(1)
        )
        if len(ratings) == 1:
            return ratings[0].mark
        return None
