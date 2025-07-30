import logging
from urllib.parse import parse_qsl

from fastapi import Depends, Request, Security
from fastapi.exceptions import HTTPException
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt

from point.config import settings
from point.errors import APIException, ErrorCode
from point.services import bs
from point.view import AuthIn, AuthUserIn
from point.view import AuthUser


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


def validate_telegram_init_data(init_data: AuthIn) -> AuthUserIn | None:
    init_data_dict = dict(parse_qsl(init_data.init_data_raw, keep_blank_values=True))
    if "user" not in init_data_dict or not bs.validate_data(data_dict=init_data_dict):
        return None

    return AuthUserIn.model_validate_json(init_data_dict["user"])
