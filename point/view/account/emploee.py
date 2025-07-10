from uuid import UUID

from pydantic import Field

from point.entity_types import PointHash, Image
from point.view import PointBase

from .purpose import Purpose, PurposeIn


class JobPlaceOut(PointBase):
    id: UUID
    name: str = Field(max_length=32)
    address: str = Field(max_length=64)


class EmployeeMeta(PointBase):
    show_job: bool = False
    show_purpose: bool = False


class EmployeePublicOut(PointBase):
    id: UUID
    profession: str = Field(max_length=32)
    photo: Image
    name: str
    job_place: JobPlaceOut | None = Field(default=None)
    purpose: Purpose | None = Field(default=None)


class EmployeeOut(EmployeePublicOut):
    first_name: str = Field(max_length=32)
    last_name: str = Field(max_length=32)
    meta: EmployeeMeta
    job_place: JobPlaceOut


class EmployeeCreateIn(PointBase):
    meta: EmployeeMeta
    first_name: str = Field(max_length=32)
    last_name: str = Field(max_length=32)


class EmployeeDbCreateIn(EmployeeCreateIn):
    job_place_id: UUID
    profession: str = Field(max_length=32)
    photo_hash: PointHash


class EmployeeUpdateIn(PointBase):
    purpose: PurposeIn | None = Field(default=None)
    meta: EmployeeMeta | None = Field(default=None)
    first_name: str | None = Field(default=None, max_length=32)
    last_name: str | None = Field(default=None, max_length=32)


class EmployeeDbUpdateIn(EmployeeUpdateIn):
    photo_hash: PointHash | None = Field(default=None)
