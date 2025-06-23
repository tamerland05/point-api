import logging

from fastapi import Depends, Request, Security
from fastapi.exceptions import HTTPException
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt

from point.config import settings
from point.errors import APIException, ErrorCode
from point.view import AuthIn
from point.view import AuthUser

import hashlib
import hmac

admin_api = APIKeyHeader(name="ApiKey", auto_error=True)


async def api_admin_key_auth(key=Security(admin_api)):
    if key != settings.ADMIN_AUTH_KEY:
        raise HTTPException(status_code=401)


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise APIException(ErrorCode.INVALID_AUTH_SCHEME)
            payload = self.verify_jwt(credentials.credentials)
            if not payload:
                raise APIException(ErrorCode.INVALID_TOKEN)
            return payload
        else:
            raise APIException(ErrorCode.INVALID_AUTH_CODE)

    @staticmethod
    def verify_jwt(jwt_token: str) -> dict | None:
        try:
            return jwt.decode(jwt_token, settings.public_key, algorithms=settings.jwt_algorithm)
        except Exception as e:
            logging.error(e)
            return None


def get_user(token_data=Depends(JWTBearer())) -> AuthUser:
    user = AuthUser.model_validate(
        {
            "id": int(token_data["id"]),
            "sessionId": token_data["iss"],
        }
    )
    return user


def validate_telegram_init_data(init_data: AuthIn) -> bool:
    if settings.bot_token != "":
        data_check_array = [
            f"{key}={value}" for key, value in init_data.model_dump(mode="json", exclude_unset=True).items()
            if key != "hash"
        ]
        data_check_array.sort()
        secret_key = hmac.new(b'WebAppData', settings.bot_token.encode('utf-8'), hashlib.sha256).digest()
        data_string = '\n'.join(data_check_array).encode('utf-8')
        calculated_hash = hmac.new(secret_key, data_string, hashlib.sha256).hexdigest()
        is_valid = hmac.compare_digest(calculated_hash, init_data.hash)
    else:
        is_valid = True

    if not is_valid:
        return False

    return True
