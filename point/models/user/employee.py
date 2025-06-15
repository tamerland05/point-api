from tortoise import Model, fields
from tortoise.fields import OnDelete


class Employee(Model):

    class Meta:
        table = "employers"

    job_place_id = fields.ForeignKeyField("models.Establishment", on_delete=OnDelete.RESTRICT, index=True)

    id = fields.UUIDField(pk=True, unique=True, index=True)
    profession = fields.CharField(max_length=32)
    purpose = fields.JSONField(null=True)
    meta = fields.JSONField()

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
