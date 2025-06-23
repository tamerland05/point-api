from tortoise import Model, fields
from tortoise.fields import OnDelete

from point.entity_types import TonAddress
from point.view import UserMeta


class User(Model):

    class Meta:
        table = "users"

    id = fields.BigIntField(pk=True, unique=True, index=True)
    first_name = fields.TextField(null=True)
    last_name = fields.TextField(null=True)
    username = fields.TextField(null=True)
    language_code = fields.TextField(null=True)
    photo_url = fields.TextField(null=True)
    is_bot = fields.BooleanField(null=True)
    is_premium = fields.BooleanField(null=True)
    allows_write_to_pm = fields.BooleanField(null=True)

    wallet: TonAddress = fields.TextField(null=True)
    bonus_balance = fields.BigIntField(default=0)
    tips_left = fields.BigIntField(default=0)
    meta: UserMeta = fields.JSONField(default={})

    employee = fields.ForeignKeyField(
        model_name="models.Employee",
        null=True,
        on_delete=OnDelete.SET_NULL,
        unique=True,
        index=True,
    )

    enabled = fields.BooleanField(default=True, index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    @property
    def name(self) -> str:
        return self.first_name + " " + self.last_name
