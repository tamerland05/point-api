from decimal import Decimal
from uuid import UUID

from point.controllers.base import BaseController
from point.errors import ErrorCode
from point.models import Establishment
from point.services import WalletService
from point.view import EstablishmentCreateIn


class EstablishmentController(BaseController[Establishment]):
    model = Establishment
    error_code = ErrorCode.ESTABLISHMENT_NOT_FOUND

    @classmethod
    async def get_establishment(cls, establishment_id: UUID) -> model:
        return await cls.get("menu", id=establishment_id, enabled=True)

    @classmethod
    async def admin_create(cls, establishment_create_in: EstablishmentCreateIn) -> Establishment:
        address, seed = await WalletService.create()

        establishment = await cls.model.create(
            **establishment_create_in.model_dump(mode="json"),
            location=(establishment_create_in.longitude, establishment_create_in.latitude),
            service_wallet=address,
            service_wallet_seed=seed,
        )
        await establishment.fetch_related("menu")

        return establishment

    @classmethod
    async def get_establishments_by_rectangle(
            cls,
            rectangle: tuple,
            limit: int | None = None,
            M: int = 100,
    ) -> list[model]:
        query = GET_ESTABLISHMENTS_RECTANGLE_SQL
        if limit is not None:
            query += f" LIMIT {limit}"

        establishments = await Establishment.raw(query % (rectangle + (M,) * 3))
        return establishments

    @classmethod
    async def get_establishments_near(
            cls,
            lon: Decimal,
            lat: Decimal,
            limit: int | None = None,
            name_contains: str | None = None,
    ) -> list[model]:
        where_clause = "WHERE enabled = TRUE"

        if name_contains is not None or name_contains == "":
            where_clause += f" AND LOWER(name) LIKE '%{name_contains.lower()}%'"

        query = f"""
            SELECT {ESTABLISHMENT_PREVIEW_FIELDS}, ST_Distance(location, ST_MakePoint({lon}, {lat})::geography) AS dist
            FROM establishments
            {where_clause}
            ORDER BY dist
        """

        if limit is not None:
            query += f" LIMIT {limit}"

        establishments = await Establishment.raw(query)
        return establishments


ESTABLISHMENT_PREVIEW_FIELDS = ", ".join(
    ["id", "name", "photo_hash", "establishment_type_id", "location", "address", "rating_sum", "rating_count"]
)

GET_ESTABLISHMENTS_RECTANGLE_SQL = f"""
    WITH
        filtered AS (
            SELECT {ESTABLISHMENT_PREVIEW_FIELDS} FROM establishments
            WHERE enabled = TRUE AND ST_Within(location::geometry, ST_MakeEnvelope(%f, %f, %f, %f, 4326))
        ),
        avg_rating AS (
            SELECT 
                (CASE WHEN SUM(rating_count) > 0 THEN SUM(rating_sum)::DECIMAL / SUM(rating_count) ELSE 0 END)
                    AS c
            FROM filtered
        ),
        ranked AS (
            SELECT
               e.*,
               (e.rating_count / (e.rating_count + %d)) *
               (CASE WHEN e.rating_count > 0 THEN e.rating_sum::DECIMAL / e.rating_count ELSE 0 END)
                   +
               (%d / (e.rating_count + %d)) * a.c AS z
            FROM filtered e, avg_rating a
        )
    SELECT * FROM ranked ORDER BY z DESC
"""
