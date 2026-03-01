import asyncio

from fastapi import APIRouter, Depends, status
from tortoise.transactions import in_transaction

from point.auth import get_user
from point.controllers import TaskController, ExecutedTaskController, UserController
from point.models import ExecutedTask
from point.view import AuthUser, TaskOut
from point_shared.entity_types import TaskIntegrationType
from point_shared.view import ExecutedTaskIn

router = APIRouter()


@router.get("s")
async def get_tasks(user: AuthUser = Depends(get_user)) -> list[TaskOut]:
    tasks = await TaskController.get_for_user(user.id)
    tasks.sort(key=lambda task: task.done)
    return TaskOut.list_validate(tasks)


@router.post("/execute")
async def execute_task(executed_task: ExecutedTaskIn, user: AuthUser = Depends(get_user)) -> int:
    executor, original_task, existing_task = await asyncio.gather(
        UserController.get_user(user.id),
        TaskController.get(id=executed_task.id, enabled=True),
        ExecutedTaskController.get_or_none(origin_id=executed_task.id, executor_id=user.id)
    )

    if existing_task is None:
        completed = False

        async with in_transaction():
            if original_task.integration_type == TaskIntegrationType.other:
                executor.tasks_bonus_balance += original_task.profit
                completed = True
                await executor.save(update_fields=["tasks_bonus_balance", "updated_at"])

            await ExecutedTask.create(origin_id=executed_task.id, executor_id=user.id, completed=completed)

    return status.HTTP_204_NO_CONTENT
