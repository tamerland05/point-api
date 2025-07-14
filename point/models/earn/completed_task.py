from uuid import UUID

from tortoise import fields, Model


class CompletedTask(Model):
    class Meta:
        table = "completed_tasks"
        unique_together = ("task", "executor")

    task_id: UUID
    task = fields.ForeignKeyField("models.Task", on_delete=fields.CASCADE)
    executor = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE)

    created_at = fields.DatetimeField(auto_now_add=True)
