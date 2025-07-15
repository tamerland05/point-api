from tortoise import Model, fields
from tortoise.fields import OnDelete

from point.entity_types import TipStatus


class Tip(Model):

    class Meta:
        table = "tips"

    id = fields.UUIDField(pk=True)

    sender = fields.ForeignKeyField("models.User")
    asset = fields.ForeignKeyField("models.Asset", on_delete=OnDelete.RESTRICT)

    establishment = fields.ForeignKeyField("models.Establishment", null=True)
    employee = fields.ForeignKeyField("models.Employee", null=True)

    fee_transaction = fields.JSONField()
    tip_transaction = fields.JSONField()
    expired_at = fields.DatetimeField()
    status = fields.CharEnumField(TipStatus, default=TipStatus.created, index=True)

    amount = fields.BigIntField()
    tips_left_amount = fields.DecimalField(max_digits=64, decimal_places=32)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    @property
    def transactions(self) -> list[dict]:
        return [self.tip_transaction, self.fee_transaction]
