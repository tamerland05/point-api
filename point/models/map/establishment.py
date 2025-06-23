from decimal import Decimal
from uuid import uuid4

from tortoise import Model, fields
from tortoise.fields import OnDelete

from point.entity_types import TonAddress
from point.models.utils import hash_to_link


class Establishment(Model):

    class Meta:
        table = "establishments"

    establishment_type = fields.ForeignKeyField("models.EstablishmentType", on_delete=OnDelete.RESTRICT)

    id = fields.UUIDField(pk=True, default=uuid4, unique=True, index=True)

    latitude = fields.DecimalField(max_digits=9, decimal_places=6)
    longitude = fields.DecimalField(max_digits=9, decimal_places=6)
    address = fields.CharField(max_length=128)

    service_wallet = fields.CharField(null=True, max_length=128)
    service_wallet_seed = fields.TextField(null=True)
    official_wallet = fields.CharField(max_length=128, null=True, default=None)

    name = fields.CharField(max_length=128)
    description = fields.CharField(max_length=512)
    channel_link = fields.CharField(max_length=512)
    icon_hash = fields.TextField()
    photo_hash = fields.TextField()
    gallery_hashes = fields.JSONField(default=[])
    menu = fields.ManyToManyField("models.MenuItem")

    rating = fields.DecimalField(max_digits=3, decimal_places=2, default=Decimal("0"))

    enabled = fields.BooleanField(default=True, index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    @property
    def position(self) -> dict:
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
        }

    @property
    def icon(self) -> str:
        return hash_to_link(self.icon_hash)

    @property
    def photo(self) -> str:
        return hash_to_link(self.photo_hash)

    @property
    def gallery(self) -> list[str]:
        return [hash_to_link(i) for i in self.gallery_hashes]

    @property
    def wallet(self) -> TonAddress | None:
        return self.official_wallet or self.service_wallet

