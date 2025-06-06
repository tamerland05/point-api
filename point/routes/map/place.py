from uuid import UUID, uuid4
from decimal import Decimal

from fastapi import APIRouter
from fastapi.params import Depends

from point.auth import get_user
from point.view import AuthUser, PointOut, PointPair, PlacePreview, NearPlaceCriteria, Cost, MenuItem, PlaceOut, fake
from point.view.utils import point_distance

router = APIRouter(tags=["Place"])


@router.post("s")
async def get_places(diagonal: PointPair, location: PointOut) -> list[PlacePreview]:
    places: list[PlacePreview] = []

    for _ in range(fake.random_int(1, 10)):
        latitude = Decimal(fake.random_int(
            min=int(diagonal.lower.latitude * 10 ** 4),
            max=int(diagonal.upper.latitude * 10 ** 4),
            step=1
        )) / Decimal(10 ** 4)
        longitude = Decimal(fake.random_int(
            min=int(diagonal.lower.longitude * 10 ** 4),
            max=int(diagonal.upper.longitude * 10 ** 4),
            step=1
        )) / Decimal(10 ** 4)

        places.append(PlacePreview(
            id=uuid4(),
            name=fake.name(),
            photo=fake.image_url(1280, 720),
            establishment_id=uuid4(),
            rating=fake.random_int(1, 5),
            position=PointOut(
                latitude=latitude,
                longitude=longitude,
                address=fake.address(),
            ),
        ))

    places.sort(key=lambda place: point_distance(location, place.position))

    return places


@router.post("s/near")
async def get_places_near(
        criteria: NearPlaceCriteria,
) -> list[PlacePreview]:
    places: list[PlacePreview] = []

    for _ in range(fake.random_int(1, 10)):
        latitude = Decimal(fake.random_int(
            min=int(criteria.location.latitude * 10 ** 4 - 1000),
            max=int(criteria.location.latitude * 10 ** 4 + 1000),
            step=1
        )) / Decimal(10 ** 4)
        longitude = Decimal(fake.random_int(
            min=int(criteria.location.longitude * 10 ** 4 - 1000),
            max=int(criteria.location.longitude * 10 ** 4 + 1000),
            step=1
        )) / Decimal(10 ** 4)

        places.append(PlacePreview(
            id=uuid4(),
            name=fake.name() + (criteria.name if criteria.name else ''),
            photo=fake.image_url(1280, 720),
            establishment_id=uuid4(),
            rating=Decimal(fake.random_int(1, 5000)) / Decimal(1000),
            position=PointOut(
                latitude=latitude,
                longitude=longitude,
                address=fake.wallet(),
            ),
        ))

    places.sort(key=lambda place: point_distance(criteria.location, place.position))

    return places


@router.post("/{place_id}")
async def get_place(place_id: UUID) -> PlaceOut:
    return PlaceOut(
        id=place_id,
        name=fake.name(),
        description=fake.text(),
        icon=fake.image_url(1280, 720),
        photo=fake.image_url(1280, 720),
        gallery=[fake.image_url(1280, 720)],
        establishment_id=uuid4(),
        rating=Decimal(fake.random_int(1, 5000)) / Decimal(1000),
        user_rating=fake.random_int(1, 5),
        menu=[MenuItem(
            title=fake.word(),
            description=fake.paragraph(),
            photo=fake.image_url(1280, 720),
            cost=Cost(
                value=fake.random_int(1, 100),
                currency=fake.currency_symbol()
            ),
        ) for _ in range(fake.random_int(1, 10))],
        position=PointOut(
            latitude=fake.latitude(),
            longitude=fake.longitude(),
            address=fake.wallet(),
        ),
    )


@router.post("/rate/{place_id}")
async def set_place_rate(place_id: UUID, mark: int, user: AuthUser = Depends(get_user)) -> None:
    return None
