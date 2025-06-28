from uuid import uuid4

from tortoise import Model, fields


class Asset(Model):

    class Meta:
        table = "assets"

    id = fields.UUIDField(pk=True, default=uuid4)

    symbol = fields.CharField(max_length=16, unique=True)
    name = fields.CharField(max_length=128)
    decimals = fields.SmallIntField(default=9)
    address = fields.CharField(max_length=128)
    image_url = fields.TextField()

    ton_price = fields.BigIntField(default=0)

    enabled = fields.BooleanField(default=True, index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
