from aiogram.types import LabeledPrice
from pydantic import Field, AnyUrl

from point_shared.view import PointBase


class InvoiceRequest(PointBase):
    title: str = Field(min_length=1, max_length=32)
    description: str = Field(min_length=1, max_length=255)
    payload: str = Field(min_length=1)
    currency: str = Field(min_length=3, max_length=3)
    prices: list[LabeledPrice] = Field(min_length=1)

    photo_url: AnyUrl | None = Field(default=None)


class StarsInvoiceRequest(InvoiceRequest):
    currency: str = "XTR"

    def __init__(self, amount: int, **data):
        data["prices"] = [LabeledPrice(amount=amount, label=data["title"])]
        super().__init__(**data)
