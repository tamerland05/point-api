from typing import Generic, TypeVar, Any, Coroutine

from tortoise.models import Model as TortoiseModel
from tortoise.queryset import QuerySet, QuerySetSingle

from point.errors import ErrorCode, APIException
from point_shared.view import PointBase

Model = TypeVar("Model", bound=TortoiseModel)


class BaseController(Generic[Model]):
    model: type[Model]
    error_code: ErrorCode = ErrorCode.ENTITY_NOT_FOUND

    @classmethod
    def get_or_none(cls, *prefetch, **filters) -> QuerySetSingle[Model | None]:
        return cls.model.get_or_none(**filters).prefetch_related(*prefetch)

    @classmethod
    async def get(cls, *prefetch, **filters) -> Model:
        res: Model | None = await cls.get_or_none(*prefetch, **filters)

        if res is None:
            raise APIException(cls.error_code)

        return res

    @classmethod
    def get_all(cls, *prefetch, **filters) -> QuerySet[Model]:
        return cls.model.filter(**filters).prefetch_related(*prefetch)

    @classmethod
    def filter(cls, *prefetch, **filters) -> QuerySet[Model]:
        return cls.model.filter(**filters).prefetch_related(*prefetch)

    @classmethod
    def create(cls, model_create_in: PointBase) -> Coroutine[Any, Any, Model]:
        return cls.model.create(**model_create_in.model_dump(mode="json"))

    @classmethod
    async def update(cls, *prefetch, model_update_in: PointBase, **filters) -> Model:
        entity: Model = await cls.get(*prefetch, **filters)

        model_update_in = model_update_in.model_dump(exclude_unset=True)
        await (
            entity
            .update_from_dict(model_update_in)
            .save(update_fields=list(model_update_in.keys()) + ["updated_at"])
        )

        return entity

    @classmethod
    async def delete(cls, **filters) -> None:
        await cls.model.filter(**filters).delete()
