from uuid import uuid4

from tortoise import Model, fields

from point.models.custom import TonAddressField


class Asset(Model):

    class Meta:
        table = "assets"

    id = fields.UUIDField(primary_key=True, default=uuid4)

    symbol = fields.CharField(max_length=16, unique=True)
    name = fields.CharField(max_length=128)
    decimals = fields.SmallIntField(default=9)
    address = TonAddressField()
    image_url = fields.TextField()

    price = fields.DecimalField(decimal_places=32, max_digits=64, default=0)
    priority = fields.SmallIntField(default=0)

    enabled = fields.BooleanField(default=True, db_index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
