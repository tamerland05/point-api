from uuid import UUID

from tortoise import Model, fields
from tortoise.fields import OnDelete


class EstablishmentRating(Model):

    class Meta:
        table = "establishment_ratings"
        indexes = [("establishment_id", "user_id", "created_at")]

    user = fields.ForeignKeyField("models.User", on_delete=OnDelete.CASCADE)
    establishment_id: UUID
    establishment = fields.ForeignKeyField("models.Establishment", on_delete=OnDelete.CASCADE)

    mark = fields.SmallIntField()
    created_at = fields.DatetimeField(auto_now_add=True)
