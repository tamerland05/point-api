from tortoise import Model, fields
from tortoise.fields import OnDelete


class Payment(Model):

    class Meta:
        table = "payments"
        indexes = [("done", "tag")]

    id = fields.UUIDField(primary_key=True)
    user = fields.ForeignKeyField("models.User", on_delete=OnDelete.CASCADE)
    user_id: int

    tag = fields.CharField(max_length=32)
    done = fields.BooleanField(default=False)

    meta = fields.JSONField()

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
