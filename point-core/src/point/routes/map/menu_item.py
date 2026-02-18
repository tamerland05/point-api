import asyncio
import random
from uuid import UUID

from fastapi import APIRouter, Depends

from point.auth import get_user
from point.config import settings
from point.controllers import MenuItemController, UserController
from point.i18 import translate
from point.services import bs
from point.view import MenuItemOut, Button, AuthUser

router = APIRouter()

REPLY_MENU_ITEM_REPLIES = ["oops", "dont_control", "bet_on", "love_or"]


@router.get("/{menu_item_id}")
async def get_menu_item(menu_item_id: UUID) -> MenuItemOut:
    menu_item = await MenuItemController.get(id=menu_item_id)
    return MenuItemOut.model_validate(menu_item)


@router.get("/share/{item_id}")
async def share_menu_item(item_id: UUID, user: AuthUser = Depends(get_user)):
    user, item = await asyncio.gather(
        UserController.get_user(user.id),
        MenuItemController.get("establishment", id=item_id)
    )

    lang = "ru"
    url = f"t.me/{settings.point_bot_name}?startapp=menu--{item.establishment.id}--{item_id}"
    share_button = Button(
        text=translate(tag_or_text="show", domain="share.menu_item.keyboards", lang=lang),
        url=url
    )
    text = translate(
        tag_or_text=random.choice(REPLY_MENU_ITEM_REPLIES),
        domain="share.menu_item.replies",
        lang=lang,
        item=item.title,
        establishment=item.establishment.name,
    )

    message_id = await bs.prepare_inline_message(
        user_id=user.id,
        text=text,
        photo=item.photo,
        buttons=[share_button],
    )

    return {"id": message_id}
