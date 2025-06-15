from enum import StrEnum
from typing import Any

from cryptography.fernet import Fernet
from pydantic_settings import BaseSettings


class AppEnv(StrEnum):
    DEV = "dev"
    PROD = "prod"


class Settings(BaseSettings, extra="allow"):
    admin_auth_key: str

    app_env: AppEnv

    public_key: str
    jwt_algorithm: str

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

    wallet_id: int
    seed: str

    encryption_key: str

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
    def merchant_cipher(self) -> Fernet:
        return Fernet(self.encryption_key.encode())

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)


settings = Settings(_env_file=".env", _env_file_encoding="utf-8")
TORTOISE_ORM = settings.tortoise_orm
