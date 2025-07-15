from uuid import UUID

from tortoise import Model, fields
from tortoise.fields import OnDelete

from point.models.custom import TonAddressField, BigIntDecimalField


class User(Model):

    class Meta:
        table = "users"

    id = fields.BigIntField(pk=True)
    first_name = fields.TextField(null=True)
    last_name = fields.TextField(null=True)
    username = fields.TextField(null=True)
    language_code = fields.TextField(null=True)
    photo_url = fields.TextField(null=True)

    wallet = TonAddressField(null=True)
    bonus_balance = fields.BigIntField(default=0, index=True)
    tips_left = BigIntDecimalField(default=0, index=True)
    meta = fields.JSONField(default={})

    employee_id: UUID
    employee = fields.ForeignKeyField(
        model_name="models.Employee",
        null=True,
        on_delete=OnDelete.SET_NULL,
        unique=True,
        related_name="user",
    )

    enabled = fields.BooleanField(default=True, index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    @property
    def name(self) -> str:
        return (self.first_name or "") + " " + (self.last_name or "")
