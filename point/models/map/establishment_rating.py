from tortoise import Model, fields
from tortoise.fields import OnDelete


class EstablishmentRating(Model):

    class Meta:
        table = "establishment_ratings"

    id = fields.UUIDField(pk=True)
    user = fields.ForeignKeyField("models.User", on_delete=OnDelete.CASCADE)
    place = fields.ForeignKeyField("models.Establishment", on_delete=OnDelete.CASCADE, index=True)

    mark = fields.SmallIntField()
    created_at = fields.DatetimeField(auto_now_add=True)
