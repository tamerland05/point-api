from enum import Enum
from types import DynamicClassAttribute
from typing import Any

from fastapi import status as st
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
    message: str
    code: int


class Error:
    message: str | None = None
    code: int = st.HTTP_400_BAD_REQUEST

    def __init__(self, message: str | None = None, code: int = st.HTTP_400_BAD_REQUEST):
        self.message = message
        self.code = code

    @DynamicClassAttribute
    def name(self) -> str:
        return str(self._name_).replace("_", "-")

    @staticmethod
    def responses(*args) -> dict[str, Any]:  # type: ignore
        rsp: dict[str, Any] = {"model": ErrorResponse, "description": args if len(args) == 1 else "Bad Request"}
        if len(args) == 1:
            return {
                "model": ErrorResponse,
                "description": "Bad Request",
                "errors": {i.name: i.value.message if isinstance(i.value, Error) else i.value for i in args},
            }

        for arg in args:
            value = arg.value.message if isinstance(arg.value, Error) else arg.value
            rsp["errors"] = [rsp["errors"], {arg.name: value}] if "errors" in rsp else {arg.name: value}
        return rsp


class ErrorCodeBase(Error, Enum):
    def __new__(cls, message: str, status_code: int = st.HTTP_400_BAD_REQUEST) -> Error:
        return Error(message, status_code)
