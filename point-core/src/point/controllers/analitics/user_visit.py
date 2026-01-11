import logging
from uuid import UUID

from point.controllers.base import BaseController
from point.models import UserVisit


class UserVisitController(BaseController[UserVisit]):
    @classmethod
    async def add_user_visit(cls, user_id: int, establishment_id: UUID) -> None:
        try:
            await UserVisit.raw(ADD_USER_VISIT_SQL % (user_id, establishment_id))
        except Exception as e:
            logging.exception(f"Exception while adding user visit: {e}")


ADD_USER_VISIT_SQL = """
    INSERT INTO user_visits (user_id, establishment_id, visits)
    VALUES (%d, '%s', 1)
    ON CONFLICT (user_id, establishment_id) 
    DO UPDATE SET visits = user_visits.visits + 1;
"""