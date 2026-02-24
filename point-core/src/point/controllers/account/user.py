from uuid import UUID

from tortoise.transactions import in_transaction

from point.config import settings
from point.controllers.base import BaseController
from point.errors import ErrorCode
from point.models import User, Referral, Employee
from point.view import AuthUserIn


class UserController(BaseController[User]):
    error_code: ErrorCode = ErrorCode.USER_NOT_FOUND
    model = User

    @classmethod
    async def get_or_create_user(cls, user_in: AuthUserIn) -> tuple[model, bool]:
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
    def validate_meta(cls, user: model) -> None:
        if "show_tips_left" not in user.meta or not user.meta["show_tips_left"]:
            user.tips_left = None

    @classmethod
    async def create_referral(cls, referrer_id: int, user_id: int, is_premium: bool) -> None:
        async with in_transaction():
            referrer = await cls.get_or_none(id=referrer_id, enabled=True)
            if referrer is None:
                return
            await Referral.create(referral_id=user_id, referrer_id=referrer_id)
            referrer.referrals_bonus_balance += (
                settings.bonus_reward_for_premium if is_premium
                else settings.bonus_reward_for_simple
            )
            await referrer.save(update_fields=["referrals_bonus_balance", "updated_at"])

    @classmethod
    async def find_referrals(
            cls,
            referrer_id: int,
            page: int,
            size: int,
    ) -> list[model]:
        offset = (page - 1) * size
        return await User.raw(SELECT_REFERRALS_SQL % (referrer_id, size, offset))

    @classmethod
    async def count_referrals(cls, referrer_id: int) -> int:
        return await Referral.filter(referrer_id=referrer_id).count()

    @classmethod
    async def get_top_users(cls) -> list[model]:
        users: list[cls.model] = await cls.model.raw(GET_TOP_USERS_SQL)
        employees = await Employee.filter(id__in=[u.employee_id for u in users if u.employee_id]).prefetch_related("job_place")
        employees = {e.id: e for e in employees}

        for user in users:
            if user.employee_id in employees:
                user.employee = employees[user.employee_id]
            else:
                user.employee = None

        return users

    @classmethod
    async def update_user_ranks(cls):
        await cls.model.raw(UPDATE_RANKS_SQL)


BONUS_BALANCE_SUM = "(u.tasks_bonus_balance + u.tips_bonus_balance + u.referrals_bonus_balance)"

UPDATE_RANKS_SQL = f"""
    UPDATE users u SET rank = ranked.rank
    FROM (SELECT id, ROW_NUMBER() OVER (ORDER BY {BONUS_BALANCE_SUM} DESC, id) AS rank FROM users) AS ranked
    WHERE u.id = ranked.id 
"""

SELECT_REFERRALS_SQL = f"""
    SELECT u.*
    FROM referrals r JOIN users u ON u.id = r.referral_id
    WHERE r.referrer_id = %s
    ORDER BY {BONUS_BALANCE_SUM} DESC
    LIMIT %s OFFSET %s
"""

GET_TOP_USERS_SQL = f"""
    SELECT u.*
    FROM users u
    WHERE u.enabled
    ORDER BY {BONUS_BALANCE_SUM} DESC, u.id
    LIMIT 100
"""