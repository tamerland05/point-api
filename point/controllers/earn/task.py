from point.controllers.base import BaseController
from point.errors import ErrorCode
from point.models import Task, CompletedTask


class TaskController(BaseController[Task]):
    error_code = ErrorCode.TASK_NOT_FOUND
    model = Task

    @classmethod
    async def get_for_user(cls, user_id: int) -> list[Task]:
        tasks = await cls.model.filter(enabled=True)
        completed_tasks = await CompletedTask.filter(executor_id=user_id, task_id__in=[t.id for t in tasks])
        completed_tasks_ids = [t.task_id for t in completed_tasks]

        for task in tasks:
            if task.id in completed_tasks_ids:
                task.done = True

        return tasks
