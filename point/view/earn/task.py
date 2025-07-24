from uuid import UUID

from pydantic import Field, AnyUrl

from point.entity_types import Image
from point.view import PointBase


class TaskOut(PointBase):
    id: UUID
    title: str = Field(max_length=128)
    description: str = Field(max_length=512)
    icon: Image
    link: AnyUrl = Field(max_length=1024)
    profit: int = Field(gt=0)
    done: bool = Field(default=False)

