from fastapi import APIRouter, Depends

from point.auth import get_user
from point.controllers import InvitationController
from point.view import AuthUser, InvitationOut

router = APIRouter()


@router.get("")
async def get_invitation(user: AuthUser = Depends(get_user)) -> InvitationOut:
    invitation = await InvitationController.get(user_id=user.id)
    return InvitationOut.model_validate(invitation)
