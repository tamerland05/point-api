from uuid import UUID

from fastapi import APIRouter

from point.controllers import MenuItemController
from point.view import MenuItemOut

router = APIRouter()


@router.get("/{menu_item_id}")
async def get_menu_item(menu_item_id: UUID) -> MenuItemOut:
    menu_item = await MenuItemController.get(id=menu_item_id)
    return MenuItemOut.model_validate(menu_item)
