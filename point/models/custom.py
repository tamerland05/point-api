from decimal import Decimal

from tortoise.fields import Field, TextField, BigIntField, SmallIntField, IntField

from point.entity_types import TonAddress


class ScaledDecimalField(Field):
    multiplier = Decimal("1e32")

    def __init__(self, multiplier: int | None = None, **kwargs):
        super().__init__(**kwargs)
        if multiplier is not None:
            self.multiplier = Decimal(f"1e{multiplier}")

    def to_db_value(self, value: int | float | Decimal | None, instance) -> int | None:
        if value is None:
            return None
        return int(value * self.multiplier)

    def to_python_value(self, value: int) -> Decimal | None:
        if value is None:
            return None
        return value / self.multiplier


class BigIntDecimalField(ScaledDecimalField, BigIntField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class IntDecimalField(ScaledDecimalField, IntField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class SmallIntDecimalField(ScaledDecimalField, SmallIntField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class TonAddressField(TextField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_db_value(self, value: TonAddress | None, instance) -> str | None:
        if value is None:
            return None
        return value.root

    def to_python_value(self, value: str) -> TonAddress | None:
        if value is None:
            return None
        return TonAddress(root=value)
