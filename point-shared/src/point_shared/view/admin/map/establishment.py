from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field, AnyUrl

from point_shared.entity_types import PointHash, TonAddress, EstablishmentOrderColumn, SortOrder
from point_shared.view import PointBase, EstablishmentOut


class EstablishmentCreateIn(PointBase):
    establishment_type_id: UUID

    latitude: Decimal = Field(ge=-90, le=90)
    longitude: Decimal = Field(ge=-180, le=180)
    address: str = Field(max_length=128)

    name: str = Field(max_length=128)
    description: str = Field(max_length=512)
    channel_link: AnyUrl | None = Field(default=None, max_length=512)
    icon_hash: PointHash
    photo_hash: PointHash
    gallery_hashes: list[PointHash] = Field(default_factory=list)


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
    gallery_hashes: list[PointHash] | None = Field(default=None)

    enabled: bool | None = Field(default=None)


class EstablishmentAdminOut(EstablishmentOut):
    service_wallet: TonAddress | None = Field(default=None)
    service_wallet_seed: str | None = Field(default=None)
    official_wallet: TonAddress | None = Field(default=None)

    icon_hash: PointHash = Field(default=None)
    photo_hash: PointHash = Field(default=None)

    enabled: bool
    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)


class EstablishmentSortOrder(PointBase):
    field: EstablishmentOrderColumn
    order: SortOrder


class EstablishmentCriteria(PointBase):
    name_contains: str | None = Field(default=None)
    establishment_type_id: UUID | None = Field(default=None)

    page: int = Field(default=1)
    size: int = Field(default=100)

    sort: list[EstablishmentSortOrder] | None = Field(default=None)
