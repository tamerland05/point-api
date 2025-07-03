from uuid import uuid4

from tortoise import Model, fields
from tortoise.fields import OnDelete

from point.models.utils import hash_to_link


class Employee(Model):

    class Meta:
        table = "employers"

    job_place = fields.ForeignKeyField("models.Establishment", on_delete=OnDelete.RESTRICT)

    id = fields.UUIDField(pk=True, default=uuid4)
    profession = fields.CharField(max_length=32)
    first_name = fields.CharField(max_length=32)
    last_name = fields.CharField(max_length=32)
    photo_hash = fields.TextField()
    purpose = fields.JSONField()
    meta = fields.JSONField()

    enabled = fields.BooleanField(default=True, index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    @property
    def photo(self) -> str:
        return hash_to_link(self.photo_hash)

    @property
    def name(self) -> str:
        return self.first_name + " " + self.last_name
