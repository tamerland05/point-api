from point.controllers.base import BaseController
from point.errors import ErrorCode
from point.models import EstablishmentRating


class EstablishmentRatingController(BaseController[EstablishmentRating]):
    model = EstablishmentRating
    error_code = ErrorCode.ESTABLISHMENT_RATING_NOT_FOUND
