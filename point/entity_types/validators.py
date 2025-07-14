from typing import Self

from pydantic import UrlConstraints, AnyUrl, RootModel, Field, model_validator
from pytoniq_core import Address, AddressError


class Image(AnyUrl):
    _constraints = UrlConstraints(max_length=1024, allowed_schemes=["http", "https"])


class PointRoot[T](RootModel[T]):
    root: T = Field(..., kw_only=True)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.root!r})"

    def __str__(self) -> str:
        return str(self.root)


class PointName(PointRoot[str]):
    root: str = Field(max_length=32, kw_only=True)


class PointDescription(PointRoot[str]):
    root: str = Field(max_length=256, kw_only=True)


class PointHash(PointRoot[str]):
    root: str = Field(min_length=32, max_length=32 + 8, kw_only=True)


class PointBlockchainHash(PointRoot[str]):
    root: str = Field(min_length=44, max_length=44, kw_only=True)


class TonAddress(PointRoot[str]):
    root: str = Field(max_length=256, kw_only=True)

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        try:
            addr = Address(address=self.root)
        except AddressError:
            raise ValueError("Address is not a valid address")

        self.root = addr.to_str(
            is_user_friendly=True,
            is_url_safe=True,
            is_bounceable=False
        )
        return self
