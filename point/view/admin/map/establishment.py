from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field, AnyUrl

from point.entity_types import PointHash
from point.view import PointBase, PointUploadIn, EstablishmentOut


class EstablishmentCreateIn(PointBase):
    establishment_type_id: UUID

    position: PointUploadIn

    name: str = Field(max_length=128)
    description: str = Field(max_length=512)
    channel_link: AnyUrl | None = Field(default=None, max_length=512)
    icon_hash: PointHash
    photo_hash: PointHash
    gallery_hashes: list[PointHash] = Field(default_factory=list)


class EstablishmentDbCreateIn(EstablishmentCreateIn):
    address: str = Field(max_length=128)

    @property
    def location(self) -> tuple[Decimal, Decimal]:
        return self.position.longitude, self.position.latitude


class EstablishmentUpdateIn(PointBase):
    establishment_type_id: UUID | None = Field(default=None)

    latitude: Decimal | None = Field(default=None, ge=-90, le=90)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180)
    address: str | None = Field(default=None, max_length=128)

    name: str | None = Field(default=None, max_length=128)
    description: str | None = Field(default=None, max_length=512)
    channel_link: AnyUrl | None = Field(default=None, max_length=512)
    icon_hash: PointHash | None = Field(default=None)
    photo_hash: PointHash | None = Field(default=None)
    gallery: list[PointHash] | None = Field(default=None)

    enabled: bool | None = Field(default=None)


class EstablishmentAdminOut(EstablishmentOut):
    service_wallet: str | None = Field(default=None, max_length=128)
    service_wallet_seed: str | None = Field(default=None)
    official_wallet: str | None = Field(default=None, max_length=128)

    enabled: bool
    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)
