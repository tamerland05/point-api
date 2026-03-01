from uuid import UUID

from tortoise import fields, Model

from .task import Task
from ..account.user import User


class ExecutedTask(Model):
    class Meta:
        table = "executed_tasks"
        unique_together = ("origin", "executor")

    completed = fields.BooleanField(default=False)

    origin_id: UUID
    origin: Task = fields.ForeignKeyField("models.Task", on_delete=fields.CASCADE)

    executor_id: int
    executor: User = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE)

    created_at = fields.DatetimeField(auto_now_add=True, primary_key=True)
    updated_at = fields.DatetimeField(auto_now=True)
