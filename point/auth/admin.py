from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from point.config import settings

admin_api = APIKeyHeader(
    name="AdminApiKey",
    auto_error=True,
    scheme_name='AdminApiKey',
)


async def api_admin_key_auth(key: str = Security(admin_api)) -> None:
    if key != settings.admin_auth_key:
        raise HTTPException(status_code=401)
