from typing import Self

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from tortoise import Model


class PointBase(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True, extra="ignore")

    @classmethod
    def list_validate(cls, raw_models: list[dict | Model]) -> list[Self]:
        return [cls.model_validate(r) for r in raw_models]
