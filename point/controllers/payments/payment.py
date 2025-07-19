from point.controllers.base import BaseController
from point.errors import ErrorCode
from point.models import Payment


class PaymentController(BaseController[Payment]):
    model = Payment
    error_code = ErrorCode.PAYMENT_NOT_FOUND
