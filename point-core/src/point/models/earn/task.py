from tortoise import fields, Model

from point_shared.entity_types import TaskIntegrationType
from point.models.utils import hash_to_link


class Task(Model):
    class Meta:
        table = "tasks"

    id = fields.UUIDField(primary_key=True)
    title = fields.CharField(max_length=128)
    description = fields.CharField(max_length=512)
    profit = fields.BigIntField(ge=0)
    icon_hash = fields.CharField(max_length=128)

    link = fields.CharField(max_length=1024)
    integration_type = fields.CharEnumField(enum_type=TaskIntegrationType, default=None)
    config = fields.JSONField(null=True, default=None)

    enabled = fields.BooleanField(default=True, db_index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    done = False

    @property
    def icon(self) -> str:
        return hash_to_link(self.icon_hash)
