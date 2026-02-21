from decimal import Decimal
from uuid import UUID

from tortoise.expressions import RawSQL
from tortoise.query_utils import Prefetch

from point.controllers.base import BaseController
from point.errors import ErrorCode
from point.models import Establishment, MenuItem
from point.services import WalletService
from point.view import EstablishmentCreateIn


class EstablishmentController(BaseController[Establishment]):
    model = Establishment
    error_code = ErrorCode.ESTABLISHMENT_NOT_FOUND

    @classmethod
    async def get_establishment(cls, establishment_id: UUID) -> model:
        return await cls.get(
            Prefetch(
                "menu",
                queryset=MenuItem.filter(enabled=True)
            ),
            id=establishment_id,
            enabled=True,
        )

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
            rectangle: tuple[float, ...],
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
        query = Establishment.filter(enabled=True)

        if name_contains:
            query = query.filter(name__icontains=name_contains)

        query = query.annotate(
            distance=RawSQL("location <-> ST_MakePoint(%s, %s)::geography" % (lon, lat))
        ).order_by("distance")

        if limit:
            query = query.limit(limit)

        return await query


ESTABLISHMENT_PREVIEW_FIELDS = ", ".join(
    ["id", "name", "photo_hash", "establishment_type_id", "location", "address", "rating_sum", "rating_count"]
)

GET_ESTABLISHMENTS_RECTANGLE_SQL = f"""
    WITH
        filtered AS (
            SELECT {ESTABLISHMENT_PREVIEW_FIELDS} FROM establishments
            WHERE enabled AND ST_Within(location::geometry, ST_MakeEnvelope(%f, %f, %f, %f, 4326))
        ),
        avg_rating AS (
            SELECT
                (CASE WHEN SUM(rating_count) > 0 THEN SUM(rating_sum)::NUMERIC / SUM(rating_count) ELSE 0::NUMERIC END)
                    AS c
            FROM filtered
        ),
        ranked AS (
            SELECT
               e.*,
               (e.rating_count::NUMERIC / (e.rating_count + %d)) *
               (CASE WHEN e.rating_count > 0 THEN e.rating_sum::NUMERIC / e.rating_count ELSE 0::NUMERIC END)
                   +
               (%d::NUMERIC / (e.rating_count + %d)) * a.c AS z
            FROM filtered e, avg_rating a
        )
    SELECT * FROM ranked 
    ORDER BY z DESC, id 
"""
