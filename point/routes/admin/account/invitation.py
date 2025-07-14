import asyncio

from fastapi import APIRouter

from point.controllers import InvitationController, UserController, EstablishmentController
from point.view import InvitationCreateIn, InvitationAdminOut, InvitationDeleteIn

router = APIRouter()


@router.get("s")
async def get_all_invitations() -> list[InvitationAdminOut]:
    invitations = await InvitationController.filter()
    return InvitationAdminOut.list_validate(invitations)


@router.post("")
async def create_invitation(
        invitation_in: InvitationCreateIn,
) -> InvitationAdminOut:
    await EstablishmentController.get(id=invitation_in.establishment_id)
    invitation = await InvitationController.create(invitation_in)
    return InvitationAdminOut.model_validate(invitation)


@router.post("-delete")
async def delete_invitation(
        invitation_in: InvitationDeleteIn,
) -> None:
    await InvitationController.delete(
        user_id=invitation_in.user_id,
        establishment_id=invitation_in.establishment_id,
    )
