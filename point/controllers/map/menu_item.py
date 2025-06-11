from point.controllers.base import BaseController
from point.errors import ErrorCode
from point.models import MenuItem


class MenuItemController(BaseController[MenuItem]):
    model = MenuItem
    error_code = ErrorCode.MENU_ITEM_NOT_FOUND
