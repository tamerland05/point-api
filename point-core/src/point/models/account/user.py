from uuid import UUID

from tortoise import Model, fields
from tortoise.fields import OnDelete

from point.models.custom import TonAddressField


class User(Model):

    class Meta:
        table = "users"

    id = fields.BigIntField(primary_key=True)
    first_name = fields.TextField(null=True)
    last_name = fields.TextField(null=True)
    username = fields.TextField(null=True)
    language_code = fields.TextField(null=True)
    photo_url = fields.TextField(null=True)

    wallet = TonAddressField(null=True)
    meta = fields.JSONField(default={})

    tasks_bonus_balance = fields.BigIntField(default=0)
    tips_bonus_balance = fields.BigIntField(default=0)
    referrals_bonus_balance = fields.BigIntField(default=0)
    tips_left = fields.DecimalField(default=0, max_digits=64, decimal_places=32)
    rank = fields.BigIntField(default=0)

    employee_id: UUID | None
    employee = fields.ForeignKeyField(
        model_name="models.Employee",
        null=True,
        on_delete=OnDelete.SET_NULL,
        unique=True,
        related_name="user",
    )

    enabled = fields.BooleanField(default=True, db_index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    @property
    def name(self) -> str:
        return (self.first_name or "") + " " + (self.last_name or "")

    @property
    def bonus_balance(self) -> int:
        return self.tasks_bonus_balance + self.tips_bonus_balance + self.referrals_bonus_balance
