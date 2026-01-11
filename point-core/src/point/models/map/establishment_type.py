from uuid import uuid4

from tortoise import Model, fields

from point.models.utils import hash_to_link


class EstablishmentType(Model):

    class Meta:
        table = "establishment_types"

    id = fields.UUIDField(pk=True, default=uuid4)

    name = fields.CharField(max_length=128, unique=True)
    icon_hash = fields.TextField()
    color_code = fields.TextField(null=True)

    enabled = fields.BooleanField(default=True, index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    @property
    def icon(self) -> str:
        return hash_to_link(self.icon_hash)
