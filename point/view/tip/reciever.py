from uuid import UUID

from pydantic import Field

from point.view import PointBase


class EmployeeReceiver(PointBase):
    id: UUID
    name: str = Field(max_length=32)
    profession: str = Field(max_length=32)
    icon: str = Field(max_length=1024)


class ReceiversOut(PointBase):
    employees: list[EmployeeReceiver] = Field(default_factory=list)
