from uuid import uuid4

from tortoise import Model, fields
from tortoise.fields import OnDelete

from point.models.utils import hash_to_link


class MenuItem(Model):

    class Meta:
        table = "menu_items"
        unique_together = ("title", "establishment_id")

    establishment = fields.ForeignKeyField("models.Establishment", on_delete=OnDelete.RESTRICT)

    id = fields.UUIDField(pk=True, default=uuid4)

    title = fields.CharField(max_length=128)
    description = fields.CharField(max_length=128)
    photo_hash = fields.TextField(null=True)

    amount = fields.DecimalField(decimal_places=18, max_digits=64)
    currency = fields.CharField(max_length=8)

    enabled = fields.BooleanField(default=True, index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    @property
    def photo(self) -> str | None:
        return None if self.photo_hash is None else hash_to_link(self.photo_hash)

    @property
    def cost(self) -> dict:
        return {
            "amount": self.amount.normalize().to_eng_string(),
            "currency": self.currency
        }
