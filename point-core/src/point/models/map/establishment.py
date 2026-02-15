from decimal import Decimal
from uuid import uuid4

from tortoise import Model, fields
from tortoise.fields import OnDelete, BigIntField

from point_shared.entity_types import TonAddress
from point.models.custom import TonAddressField, GeographyPointField
from point.models.utils import hash_to_link


class Establishment(Model):

    class Meta:
        table = "establishments"

    establishment_type = fields.ForeignKeyField("models.EstablishmentType", on_delete=OnDelete.RESTRICT)

    id = fields.UUIDField(primary_key=True, default=uuid4)
    external_id = fields.BigIntField(unique=True, null=True)

    location = GeographyPointField()
    address = fields.CharField(max_length=128)

    service_wallet = TonAddressField(null=True)
    service_wallet_seed = fields.TextField(null=True)
    official_wallet = TonAddressField(null=True, default=None)

    name = fields.CharField(max_length=128)
    description = fields.CharField(max_length=512)
    channel_link = fields.CharField(null=True, max_length=512)
    icon_hash = fields.TextField()
    photo_hash = fields.TextField()
    gallery_hashes = fields.JSONField(default=[])

    rating_sum = BigIntField(default=0)
    rating_count = BigIntField(default=0)

    enabled = fields.BooleanField(default=True, db_index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    @property
    def position(self) -> dict:
        return {
            "longitude": self.location[0],
            "latitude": self.location[1],
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

    @property
    def rating(self) -> Decimal:
        if self.rating_count == 0:
            return Decimal("0")
        return (Decimal(self.rating_sum) / Decimal(self.rating_count)).quantize(Decimal('.1'))
