from uuid import UUID

from pydantic import Field

from point.entity_types import Image
from point.view import PointBase


class EmployeeReceiver(PointBase):
    id: UUID
    name: str = Field(max_length=32)
    profession: str = Field(max_length=32)
    photo: Image


class ReceiversOut(PointBase):
    employees: list[EmployeeReceiver] = Field(default_factory=list)
