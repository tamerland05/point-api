from fastapi import status

from .base import ErrorCodeBase


class ErrorCode(ErrorCodeBase):
    INVALID_AUTH_SCHEME = "Invalid authentication scheme.", status.HTTP_401_UNAUTHORIZED
    INVALID_TOKEN = "Invalid token or expired token.", status.HTTP_401_UNAUTHORIZED
    INVALID_AUTH_CODE = "Invalid authorization code.", status.HTTP_401_UNAUTHORIZED

    ACCESS_FORBIDDEN = "Access forbidden.", status.HTTP_403_FORBIDDEN

    ENTITY_NOT_FOUND = "Entity not found", status.HTTP_404_NOT_FOUND

    ESTABLISHMENT_TYPE_NOT_FOUND = "Establishment type not found", status.HTTP_404_NOT_FOUND
    ESTABLISHMENT_NOT_FOUND = "Establishment not found", status.HTTP_404_NOT_FOUND
    MENU_ITEM_NOT_FOUND = "Menu item not found", status.HTTP_404_NOT_FOUND
