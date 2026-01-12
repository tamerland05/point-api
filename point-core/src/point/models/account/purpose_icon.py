from uuid import uuid4

from tortoise import Model, fields

from point.models.utils import hash_to_link


class PurposeIcon(Model):

    class Meta:
        table = "purpose_icons"

    id = fields.UUIDField(primary_key=True, default=uuid4)

    preview_hash = fields.TextField()
    icon_hash = fields.TextField()

    enabled = fields.BooleanField(default=True, db_index=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    @property
    def icon(self) -> str:
        return hash_to_link(self.icon_hash)

    @property
    def preview(self) -> str:
        return hash_to_link(self.preview_hash)
