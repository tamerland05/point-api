from decimal import Decimal
from enum import StrEnum
from typing import Any

from cryptography.fernet import Fernet
from pydantic import AnyUrl
from pydantic_settings import BaseSettings

from point.entity_types import TonAddress, PointHash


class AppEnv(StrEnum):
    DEV = "dev"
    PROD = "prod"


class Settings(BaseSettings, extra="allow"):
    aws_service_name: str
    aws_endpoint_url: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_bucket_name: str

    postgres_user: str
    postgres_password: str
    postgres_port: int
    postgres_host: str
    postgres_db: str

    assets_url: AnyUrl
    ton_indexer_url: AnyUrl
    ton_indexer_api_key: str
    ton_indexer_rps: int

    wallet_id: int
    seed: str
    encryption_key: str

    fix_fee: Decimal
    jetton_transfer_amount: int
    point_wallet: TonAddress

    bonus_reward_for_premium: int
    bonus_reward_for_simple: int

    logo_hash: PointHash
    set_rating_amount: int

    bot_token: str
    jwt_algorithm: str
    public_key: str

    admin_auth_key: str

    app_env: AppEnv

    @property
    def tortoise_orm(self) -> dict[str, Any]:
        database_url = (
            f"postgres://"
            f"{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/"
            f"{self.postgres_db}"
        )

        return {
            "connections": {
                "default": database_url,
            },
            "apps": {
                "models": {
                    "models": ["point.models", "aerich.models"],
                    "default_connection": "default",
                },
            },
            "use_tz": True,
            "timezone": "UTC",
        }

    @property
    def fernet_cipher(self) -> Fernet:
        return Fernet(self.encryption_key.encode())

    def __init__(self):
        super().__init__(_env_file=".env", _env_file_encoding="utf-8")


settings = Settings()
TORTOISE_ORM = settings.tortoise_orm
