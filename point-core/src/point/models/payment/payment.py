from tortoise import Model, fields


class Payment(Model):

    class Meta:
        table = "payments"
        indexes = [("done", "tag")]

    id = fields.UUIDField(primary_key=True)
    tag = fields.CharField(max_length=32)
    done = fields.BooleanField(default=False)

    meta = fields.JSONField()

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
