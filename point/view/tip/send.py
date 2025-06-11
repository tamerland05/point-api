from decimal import Decimal
from uuid import UUID

from pydantic import Base64Str

from point.entity_types import TonAddress
from point.view import PointBase


class CheckoutTransferIn(PointBase):
    recipient_id: UUID
    asset_id: UUID
    amount: Decimal


class CheckoutTransferOut(PointBase):
    to: TonAddress
    value: int
    body: Base64Str
