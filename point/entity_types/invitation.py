from enum import StrEnum


class InvitationStatus(StrEnum):
    created = "created"
    accepted = "locked"
    failed = "failed"
