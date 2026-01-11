from decimal import Decimal
from uuid import UUID

from point_shared.entity_types import RecipientType
from point_shared.view import PointBase

from .transaction import TransactionOut


class CheckoutTipIn(PointBase):
    recipient_id: UUID
    recipient_type: RecipientType
    asset_id: UUID
    amount: Decimal


class CheckoutTipOut(PointBase):
    transactions: list[TransactionOut]

