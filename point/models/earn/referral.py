from tortoise import fields, Model


class Referral(Model):
    class Meta:
        table = "referrals"
        unique_together = ("referrer", "referral")

    referrer = fields.ForeignKeyField(
        "models.User",
        on_delete=fields.CASCADE,
        related_name="referrals_sent",
    )
    referral = fields.ForeignKeyField(
        "models.User",
        on_delete=fields.CASCADE,
        related_name="referrals_received",
    )

    created_at = fields.DatetimeField(auto_now_add=True)
