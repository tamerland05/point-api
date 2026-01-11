from tortoise import Model, fields
from tortoise.fields import OnDelete


class UserVisit(Model):
    class Meta:
        table = "user_visits"
        unique_together = ("user_id", "establishment_id")

    user = fields.ForeignKeyField("models.User", on_delete=OnDelete.CASCADE)
    establishment = fields.ForeignKeyField("models.Establishment", on_delete=OnDelete.CASCADE)
    visits = fields.IntField()
