from uuid import UUID

from fastapi import APIRouter

from point.controllers import TaskController
from point.view import TaskCreateIn, TaskUpdateIn, TaskAdminOut

router = APIRouter()


@router.get("/{task_id}")
async def get_task(
        task_id: UUID,
) -> TaskAdminOut:
    task = await TaskController.get(id=task_id)
    return TaskAdminOut.model_validate(task)


@router.get("s")
async def get_all_tasks() -> list[TaskAdminOut]:
    tasks = await TaskController.filter()
    return TaskAdminOut.list_validate(tasks)


@router.post("")
async def create_task(
        task_in: TaskCreateIn,
) -> TaskAdminOut:
    task = await TaskController.create(task_in)
    return TaskAdminOut.model_validate(task)


@router.put("/{task_id}")
async def update_task(
        task_id: UUID,
        task_update_in: TaskUpdateIn,
) -> TaskAdminOut:
    task = await TaskController.update(
        model_update_in=task_update_in,
        id=task_id
    )
    return TaskAdminOut.model_validate(task)


@router.delete("/{task_id}")
async def delete_task(
        task_id: UUID,
) -> None:
    await TaskController.delete(id=task_id)
