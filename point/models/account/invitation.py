from uuid import UUID

from tortoise import Model, fields
from tortoise.fields import OnDelete


class Invitation(Model):

    class Meta:
        table = "invitations"
        unique_together = ("user_id", "establishment_id")

    user_id = fields.BigIntField(index=True)

    establishment_id: UUID
    establishment = fields.ForeignKeyField("models.Establishment", on_delete=OnDelete.CASCADE)
    profession = fields.CharField(max_length=32)

    created_at = fields.DatetimeField(auto_now=True, pk=True)
    updated_at = fields.DatetimeField(auto_now_add=True)
