from uuid import UUID, uuid4

from faker import Faker
from fastapi import APIRouter

from point.view import Creator, SelectionPreview, SelectionOut, PlaceItem

fake = Faker()

router = APIRouter(tags=["Selection"])


@router.post("s")
async def get_selections() -> list[SelectionPreview]:
    selections: list[SelectionPreview] = []

    for _ in range(fake.random_int(1, 10)):
        selections.append(SelectionPreview(
            id=uuid4(),
            creator=Creator(
                name=fake.name(),
                icon=fake.image_url(1280, 720),
            ),
            main_area=fake.city(),
            name=fake.name(),
            description=fake.text(),
            icons=[fake.image_url(1280, 720) for _ in range(2)],
            places_count=0,
            preview_places_icons=[fake.image_url(1280, 720) for _ in range(3)],
        ))

    return selections


@router.post("/{selection_id}")
async def get_selection(selection_id: UUID) -> SelectionOut:
    return SelectionOut(
        id=selection_id,
        creator=Creator(
            name=fake.name(),
            icon=fake.image_url(1280, 720),
        ),
        main_area=fake.city(),
        places=[PlaceItem(
            id=uuid4(),
            name=fake.name(),
            description=fake.text(),
            icon=fake.image_url(1280, 720),
            address=fake.address(),
        ) for _ in range(fake.random_int(1, 10))],
    )
