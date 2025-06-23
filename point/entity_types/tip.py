from enum import StrEnum


class RecipientType(StrEnum):
    employee = "employee"
    establishment = "establishment"


class TipStatus(StrEnum):
    created = "created"
    accepted = "accepted"
    failed = "failed"
