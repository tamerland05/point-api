from tortoise import Model, fields
from tortoise.fields import OnDelete

from point.entity_types import TonAddress
from point.view import UserMeta


class User(Model):

    class Meta:
        table = "users"

    id = fields.BigIntField(pk=True, unique=True, index=True)
    first_name = fields.TextField()
    last_name = fields.TextField()
    username = fields.TextField()
    language_code = fields.TextField(null=True)
    photo_url = fields.TextField(null=True)
    is_bot = fields.BooleanField()
    is_premium = fields.BooleanField()
    allows_write_to_pm = fields.BooleanField()

    wallet: TonAddress = fields.TextField(null=True)
    bonus_balance = fields.BigIntField(null=True)
    tips_left = fields.BigIntField(null=True)
    meta: UserMeta = fields.JSONField()

    account_id = fields.ForeignKeyField("models.Employee", null=True, on_delete=OnDelete.SET_NULL)

    enabled = fields.BooleanField(default=True, index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    @property
    def name(self) -> str:
        return self.first_name + " " + self.last_name
