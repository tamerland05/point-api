from tortoise import Model, fields
from tortoise.fields import OnDelete


class EstablishmentRating(Model):

    class Meta:
        table = "place_ratings"
        unique_together = ("user_id", "place_id")

    user = fields.ForeignKeyField("models.User", on_delete=OnDelete.RESTRICT, index=True)
    place = fields.ForeignKeyField("models.Establishment", on_delete=OnDelete.RESTRICT, index=True)

    mark = fields.SmallIntField()
