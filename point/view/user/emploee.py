from uuid import UUID

from pydantic import Field

from point.entity_types import Image
from point.view import PointBase


class JobPlaceOut(PointBase):
    id: UUID
    name: str = Field(max_length=32)
    address: str = Field(max_length=64)


class Purpose(PointBase):
    icon: Image
    title: str = Field(max_length=32)
    description: str = Field(max_length=512)


class EmployeeMeta(PointBase):
    show_job: bool = False
    show_purpose: bool = False


class EmployeePublicOut(PointBase):
    id: UUID
    profession: str = Field(max_length=32)
    job_place: JobPlaceOut | None = Field(default=None)
    purpose: Purpose | None = Field(default=None)


class EmployeeOut(EmployeePublicOut):
    meta: EmployeeMeta


class EmployeeUpdateIn(PointBase):
    purpose: Purpose | None = Field(default=None)
    meta: EmployeeMeta | None = Field(default=None)
