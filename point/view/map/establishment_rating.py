from uuid import UUID

from pydantic import Field

from point.view import PointBase


class EstablishmentRatingCreateIn(PointBase):
    establishment_id: UUID
    mark: int = Field(ge=0, le=5)


class EstablishmentRatingDbCreateIn(EstablishmentRatingCreateIn):
    user_id: int
