import logging

from .error_code import ErrorCode


class APIException(Exception):
    error: ErrorCode

    def __init__(self, error: str | ErrorCode, status_code=None):
        if isinstance(error, str):
            self.error = getattr(ErrorCode, error, error)
        else:
            self.error = error
        self.status_code = status_code if status_code is not None else self.error.code
        logging.error(f"{self.error.name} ({self.status_code}):{self.error.message}")
