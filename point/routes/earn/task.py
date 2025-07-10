from fastapi import APIRouter, Depends

from point.auth import get_user
from point.controllers import TaskController
from point.view import AuthUser, TaskOut

router = APIRouter()


@router.get("s")
async def get_tasks(user: AuthUser = Depends(get_user)) -> list[TaskOut]:
    tasks = await TaskController.get_for_user(user.id)
    tasks.sort(key=lambda task: task.done, reverse=True)
    return TaskOut.list_validate(tasks)
