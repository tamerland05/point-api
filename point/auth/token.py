import logging

from jose import JWTError, jwt

from point.config import settings
from point.errors import APIException


def create_token(data: dict):
    to_encode = data

    # todo: make it more difficultly
    try:
        encoded_jwt = jwt.encode(to_encode, key=settings.public_key, algorithm=settings.jwt_algorithm)
    except JWTError as e:
        logging.error(e)
        raise APIException(status_code=401, error="Wrong access token")
    return encoded_jwt
