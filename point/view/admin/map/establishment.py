from decimal import Decimal
from uuid import UUID

from pydantic import Field, AnyUrl

from point.entity_types import PointHash
from point.view import PointBase, PointUploadIn


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
    latitude: Decimal = Field(ge=-90, le=90)
    longitude: Decimal = Field(ge=-180, le=180)
    address: str = Field(max_length=128)


class EstablishmentUpdateIn(PointBase):
    establishment_type_id: UUID | None = None

    latitude: Decimal | None = Field(default=None, ge=-90, le=90)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180)
    address: str | None = Field(default=None, max_length=128)

    name: str | None = Field(default=None, max_length=128)
    description: str | None = Field(default=None, max_length=512)
    channel_link: AnyUrl | None = Field(default=None, max_length=512)
    icon_hash: PointHash | None = None
    photo_hash: PointHash | None = None
    gallery: list[PointHash] | None = None
