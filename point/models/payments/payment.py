from tortoise import Model, fields


class Payment(Model):

    class Meta:
        table = "payments"

    id = fields.UUIDField(pk=True)
    tag = fields.TextField()
    done = fields.BooleanField(default=False)

    meta = fields.JSONField()

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
