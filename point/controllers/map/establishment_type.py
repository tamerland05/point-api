from point.controllers.base import BaseController
from point.errors import ErrorCode
from point.models import EstablishmentType


class EstablishmentTypeController(BaseController[EstablishmentType]):
    model = EstablishmentType
    error_code = ErrorCode.ESTABLISHMENT_TYPE_NOT_FOUND
