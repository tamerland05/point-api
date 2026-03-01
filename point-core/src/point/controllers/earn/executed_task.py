from datetime import datetime, UTC, timedelta

from tortoise.transactions import in_transaction

from point.controllers.base import BaseController
from point.models import Task, ExecutedTask
from point.services import cbs
from point_shared.entity_types import TaskIntegrationType
from point_shared.view import TgMembershipConfig


class ExecutedTaskController(BaseController[Task]):
    model = ExecutedTask

    @classmethod
    async def check_tg_tasks(cls) -> None:
        tasks = await (
            cls.model
            .filter(completed=False, origin__integration_type=TaskIntegrationType.tg_membership)
            .select_for_update(of=("executed_tasks",))
            .prefetch_related("origin", "executor")
        )

        for task in tasks:
            await cls.check_tg_task(task)

    @staticmethod
    async def check_tg_task(task: ExecutedTask) -> None:
        config = TgMembershipConfig.model_validate(task.origin.config)

        for oid in config.ids:
            is_member = await cbs.is_user_member_of_chat(user_id=task.executor_id, object_id=oid)
            if not is_member:
                if datetime.now(UTC) - task.created_at > timedelta(minutes=10):
                    await task.delete()
                return

        task.completed = True
        task.executor.tasks_bonus_balance += task.origin.profit

        async with in_transaction():
            await task.save(update_fields=["completed", "updated_at"])
            await task.executor.save(update_fields=["tasks_bonus_balance", "updated_at"])
