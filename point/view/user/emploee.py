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
    job_place: JobPlaceOut | None = None
    purpose: Purpose | None = None


class EmployeeOut(EmployeePublicOut):
    meta: EmployeeMeta


class EmployeeUpdateIn(PointBase):
    purpose: Purpose | None = None
    meta: EmployeeMeta | None = None
