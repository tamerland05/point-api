from typing import Generic, TypeVar
from uuid import UUID

from tortoise.models import Model as TortoiseModel

from point.errors import ErrorCode, APIException
from point.view import PointBase

Model = TypeVar("Model", bound=TortoiseModel)


class BaseController(Generic[Model]):
    model: type[Model]
    error_code: ErrorCode = ErrorCode.ENTITY_NOT_FOUND

    @classmethod
    async def get_or_none(cls, *prefetch, **filters) -> Model | None:
        return await cls.model.get_or_none(**filters).prefetch_related(*prefetch)

    @classmethod
    async def get(cls, *prefetch, **filters) -> Model:
        res: Model | None = await cls.get_or_none(*prefetch, **filters)

        if res is None:
            raise APIException(cls.error_code)

        return res

    @classmethod
    async def get_all(cls, *prefetch, **filters) -> list[Model]:
        return await cls.model.filter(**filters).prefetch_related(*prefetch)

    @classmethod
    async def filter(cls, *prefetch, **filters) -> list[Model]:
        return await cls.model.filter(**filters).prefetch_related(*prefetch)

    @classmethod
    async def create(cls, model_create_in: PointBase) -> Model:
        return await cls.model.create(**model_create_in.model_dump(mode="json"))

    @classmethod
    async def update(cls, *prefetch, model_update_in: PointBase, **filters) -> Model:
        entity: Model = await cls.get(*prefetch, **filters)
        await entity.update_from_dict(model_update_in.model_dump(exclude_unset=True)).save()

        return entity

    @classmethod
    async def delete_by_uuid(cls, model_id: UUID) -> None:
        entity: Model = await cls.get(id=model_id)
        await entity.delete()
