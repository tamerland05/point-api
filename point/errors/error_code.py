from fastapi import status

from .base import ErrorCodeBase


class ErrorCode(ErrorCodeBase):
    WRONG_CREDENTIALS = "Wrong credentials", status.HTTP_401_UNAUTHORIZED
    INVALID_AUTH_SCHEME = "Invalid authentication scheme.", status.HTTP_401_UNAUTHORIZED
    INVALID_TOKEN = "Invalid token or expired token.", status.HTTP_401_UNAUTHORIZED
    INVALID_AUTH_CODE = "Invalid authorization code.", status.HTTP_401_UNAUTHORIZED

    ACCESS_FORBIDDEN = "Access forbidden.", status.HTTP_403_FORBIDDEN

    ENTITY_NOT_FOUND = "Entity not found", status.HTTP_404_NOT_FOUND

    ESTABLISHMENT_TYPE_NOT_FOUND = "Establishment type not found", status.HTTP_404_NOT_FOUND
    ESTABLISHMENT_NOT_FOUND = "Establishment not found", status.HTTP_404_NOT_FOUND
    ESTABLISHMENT_RATING_NOT_FOUND = "Establishment rating not found", status.HTTP_404_NOT_FOUND
    MENU_ITEM_NOT_FOUND = "Menu item not found", status.HTTP_404_NOT_FOUND

    ASSET_NOT_FOUND = "Asset not found", status.HTTP_404_NOT_FOUND
    USER_ASSET_NOT_FOUND = "User asset not found", status.HTTP_404_NOT_FOUND
    TIP_NOT_FOUND = "Tip not found", status.HTTP_404_NOT_FOUND

    PURPOSE_ICON_NOT_FOUND = "Purpose icon not found", status.HTTP_404_NOT_FOUND
    EMPLOYEE_NOT_FOUND = "Employee not found", status.HTTP_404_NOT_FOUND
    INVITATION_NOT_FOUND = "Invitation not found", status.HTTP_404_NOT_FOUND
    USER_NOT_FOUND = "User not found", status.HTTP_404_NOT_FOUND
    USER_HAVE_NOT_WALLET = "User have not wallet", status.HTTP_404_NOT_FOUND

    TASK_NOT_FOUND = "Task not found", status.HTTP_404_NOT_FOUND

    PAYMENT_NOT_FOUND = "Payment not found", status.HTTP_404_NOT_FOUND
