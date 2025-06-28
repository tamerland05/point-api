from uuid import UUID

from fastapi import APIRouter

from point.controllers import EstablishmentController, MenuItemController
from point.view import MenuItemCreateIn, MenuItemOut, MenuItemDbCreateIn, MenuItemUpdateIn

router = APIRouter()


@router.get("/{menu_item_id}")
async def get_menu_item(
        menu_item_id: UUID,
) -> MenuItemOut:
    menu_item = await MenuItemController.get(id=menu_item_id)
    return MenuItemOut.model_validate(menu_item)


@router.get("s")
async def get_all_menu_items() -> list[MenuItemOut]:
    menu_items = await MenuItemController.filter()
    return [MenuItemOut.model_validate(m) for m in menu_items]


@router.post("")
async def create_menu_item(
        menu_item_in: MenuItemCreateIn,
) -> MenuItemOut:
    establishment = await EstablishmentController.get(id=menu_item_in.establishment_id)

    menu_item_in = MenuItemDbCreateIn(
        **menu_item_in.model_dump(),
        **menu_item_in.cost.model_dump(),
    )
    menu_item = await MenuItemController.create(menu_item_in)

    await establishment.menu.add(menu_item)

    return MenuItemOut.model_validate(menu_item)


@router.put("/{menu_item_id}")
async def update_menu_item(
        menu_item_id: UUID,
        menu_item_update_in: MenuItemUpdateIn,
) -> MenuItemOut:
    if menu_item_update_in.establishment_id is not None:
        await EstablishmentController.get(id=menu_item_update_in.establishment_id)

    menu_item = await MenuItemController.update(
        model_update_in=menu_item_update_in,
        id=menu_item_id
    )
    return MenuItemOut.model_validate(menu_item)


@router.delete("/{menu_item_id}")
async def delete_menu_item(
        menu_item_id: UUID,
) -> None:
    await MenuItemController.delete_by_uuid(model_id=menu_item_id)
