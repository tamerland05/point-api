from pydantic import Field

from point_shared.entity_types import Image
from point_shared.view import PointBase


class EmployeeReceiver(PointBase):
    id: int
    name: str = Field(max_length=32)
    profession: str = Field(max_length=32)
    photo: Image


class ReceiversOut(PointBase):
    employees: list[EmployeeReceiver] = Field(default_factory=list)
