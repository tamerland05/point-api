from typing import Self

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class PointBase(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True, extra="ignore")

    @classmethod
    def list_validate(cls, raw_models: list) -> list[Self]:
        return [cls.model_validate(r) for r in raw_models]
