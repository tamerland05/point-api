from uuid import UUID

from tortoise.transactions import in_transaction

from point.config import settings
from point.controllers.base import BaseController
from point.errors import ErrorCode
from point.models import User, Referral
from point.view import AuthUserIn


class UserController(BaseController[User]):
    error_code: ErrorCode = ErrorCode.USER_NOT_FOUND
    model = User

    @classmethod
    async def get_or_create_user(cls, user_in: AuthUserIn) -> (model, bool):
        user = await cls.get_or_none(id=user_in.id, enabled=True)
        created = False

        if user is None:
            user = await UserController.create(model_create_in=user_in)
            created = True

        return user, created

    @classmethod
    async def get_user(cls, user_id: int) -> model:
        user = await cls.get("employee", "employee__job_place", id=user_id, enabled=True)

        if user.employee_id is None:
            user.employee = None

        return user

    @classmethod
    async def get_by_employee(cls, employee_id: UUID) -> model:
        return await cls.get(employee_id=employee_id, enabled=True)

    @classmethod
    async def find_by_employee_ids(cls, employee_ids: list[UUID]) -> list:
        return await cls.filter(employee_id__in=employee_ids).values_list("employee_id", "id")

    @classmethod
    def validate_meta(cls, user: model) -> None:
        if "show_tips_left" not in user.meta or not user.meta["show_tips_left"]:
            user.tips_left = None

    @classmethod
    async def create_referral(cls, referrer_id: int, user_id: int, is_premium: bool) -> None:
        async with in_transaction():
            referrer = await cls.get_or_none(id=referrer_id, enabled=True)
            if referrer is None:
                return
            await Referral.create(user_id=user_id, referral_id=user_id, referrer_id=referrer_id)
            referrer.bonus_balance += (
                settings.bonus_reward_for_premium if is_premium
                else settings.bonus_reward_for_simple
            )
            await referrer.save(update_fields=["bonus_balance", "updated_at"])

    @classmethod
    async def find_referrals(
            cls,
            referrer_id: int,
            page: int,
            size: int,
    ) -> list[model]:
        offset = (page - 1) * size

        referral_references = await (
            Referral.filter(referrer_id=referrer_id)
            .prefetch_related("referral")
            .offset(offset)
            .limit(size)
            .order_by("-referral__bonus_balance")
        )
        return [referral_reference.referral for referral_reference in referral_references]

    @classmethod
    async def count_referrals(cls, referrer_id: int) -> int:
        return await Referral.filter(referrer_id=referrer_id).count()

    @classmethod
    async def get_top_users(cls) -> list[model]:
        return await (
            cls.filter("employee", "employee__job_place", enabled=True)
            .order_by("-bonus_balance")
            .limit(100)
        )

    @classmethod
    async def update_user_ranks(cls):
        await cls.model.raw(UPDATE_RANKS_SQL)


UPDATE_RANKS_SQL = """
    UPDATE users u SET rank = ranked.rank
    FROM (SELECT id, ROW_NUMBER() OVER (ORDER BY bonus_balance DESC, id) AS rank
            FROM users) AS ranked
    WHERE u.id = ranked.id 
"""
