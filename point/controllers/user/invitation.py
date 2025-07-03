from point.controllers.base import BaseController
from point.errors import ErrorCode
from point.models import Invitation


class InvitationController(BaseController[Invitation]):
    model = Invitation
    error_code = ErrorCode.INVITATION_NOT_FOUND
