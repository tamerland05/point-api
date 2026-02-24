import asyncio
import datetime
import logging
import uuid
from decimal import ROUND_HALF_UP, Decimal

from tortoise.transactions import in_transaction

from point.config import settings
from point.controllers.base import BaseController
from point.controllers import EstablishmentController, UserController
from point_shared.entity_types import RecipientType, TipStatus
from point.i18 import translate
from point.errors import ErrorCode, APIException
from point.models import Tip
from point.services import tns, bs
from point.view import CheckoutTipIn, TransactionDbOut

from .asset import AssetController


class TipController(BaseController[Tip]):
    model = Tip
    error_code: ErrorCode = ErrorCode.TIP_NOT_FOUND

    bonus_ranges = [
        (1, 4, 100),
        (5, 9, 500),
        (10, 19, 1_500),
        (20, 49, 3_000),
        (50, 99, 7_500),
        (100, float("inf"), 15_000),
    ]

    @classmethod
    async def create_tip(cls, checkout_in: CheckoutTipIn, sender_id: int) -> model:
        sender, asset, ton, recipient = await asyncio.gather(
            UserController.get_user(user_id=sender_id),
            AssetController.get_asset(asset_id=checkout_in.asset_id),
            AssetController.get_ton(),
            EstablishmentController.get_establishment(establishment_id=checkout_in.recipient_id)
            if checkout_in.recipient_type == RecipientType.establishment
            else UserController.get_by_employee(employee_id=checkout_in.recipient_id)
        )
        if sender.wallet is None:
            raise APIException(ErrorCode.USER_HAVE_NOT_WALLET)

        tip_id = uuid.uuid4()
        asset_amount = int(checkout_in.amount * (10 ** asset.decimals))
        supposed_fee = asset_amount // 10
        tips_left_amount = checkout_in.amount * asset.price
        payload = str(tip_id)

        def ton_trx_fun(amount, destination_address):
            return tns.create_ton_transfer(
                sender_address=sender.wallet,
                destination_address=destination_address,
                ton_amount=amount,
                payload=payload,
            )

        def jetton_trx_fun_builder(sender_jetton_wallet_address):
            return lambda amount, destination_address: tns.create_jetton_transfer(
                sender_address=sender.wallet,
                sender_jetton_wallet_address=sender_jetton_wallet_address,
                destination_address=destination_address,
                jetton_amount=amount,
                payload=payload,
            )

        trx_fun = ton_trx_fun
        if asset.symbol != "TON":
            try:
                sender_jetton_wallet = await tns.get_jetton(
                    jetton_master=asset.address,
                    owner_address=sender.wallet,
                )
            except Exception as e:
                logging.exception(f"Exception while fetch info about user asset {e}")
                raise APIException(ErrorCode.USER_ASSET_NOT_FOUND)
            trx_fun = jetton_trx_fun_builder(sender_jetton_wallet.address)

        if tips_left_amount < settings.fix_fee:
            fee_transaction = tns.create_ton_transfer(
                sender_address=sender.wallet,
                destination_address=settings.point_wallet,
                ton_amount=settings.fix_fee * 10 ** 9 // ton.price,
                payload=payload,
            )
            supposed_fee = 0
            tips_left_amount += settings.fix_fee
        else:
            fee_transaction = trx_fun(supposed_fee, settings.point_wallet)

        tip_transaction = trx_fun(asset_amount - supposed_fee, recipient.wallet)

        tip = await cls.model.create(
            id=tip_id,
            sender_id=sender_id,
            employee_id=checkout_in.recipient_id if checkout_in.recipient_type == RecipientType.employee else None,
            establishment_id=checkout_in.recipient_id if checkout_in.recipient_type != RecipientType.employee else None,
            asset=asset,
            fee_transaction=fee_transaction.model_dump(mode="json"),
            tip_transaction=tip_transaction.model_dump(mode="json"),
            expired_at=(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)),
            amount=asset_amount - supposed_fee,
            tips_left_amount=tips_left_amount
        )

        return tip

    @classmethod
    async def pooling_tips(cls):
        tips = await cls.filter(status=TipStatus.created)

        for t in tips:
            try:
                await cls._check_tip_completion(tip=t)
            except Exception as e:
                logging.error(f"error while pooling tip {t.id}")
                logging.exception(e)

    @classmethod
    async def _check_tip_completion(cls, tip: Tip) -> None:
        is_completed = all(await asyncio.gather(
                tns.is_transaction_completed(
                    transaction=TransactionDbOut.model_validate(tip.fee_transaction),
                ),
                tns.is_transaction_completed(
                    transaction=TransactionDbOut.model_validate(tip.tip_transaction),
                )
        ))

        if is_completed:
            await cls._on_tip_completion(tip=tip)
        elif tip.expired_at <= datetime.datetime.now(datetime.timezone.utc):
            tip.status = TipStatus.failed
            await tip.save(update_fields=["status", "updated_at"])

    @classmethod
    async def _on_tip_completion(cls, tip: model) -> None:
        tip.status = TipStatus.accepted

        async with in_transaction():
            await tip.fetch_related("sender")
            tip.sender.tips_bonus_balance += cls.calculate_bonus(tip.tips_left_amount)
            tip.sender.tips_left += tip.tips_left_amount
            await tip.save(update_fields=["status", "updated_at"])
            await tip.sender.save(update_fields=["tips_bonus_balance", "tips_left", "updated_at"])

        if tip.employee_id is None:
            return

        try:
            await cls.notify_employee(tip)
        except Exception as e:
            logging.exception(f"error while notify employee {tip.id}: {e}")

    @staticmethod
    async def notify_employee(tip: model) -> None:
        await tip.fetch_related("sender", "asset", "employee", "employee__user")
        if len(tip.employee.user) != 1:
            return
        employee = tip.employee.user[0]
        amount = (
            (tip.amount / Decimal(10 ** tip.asset.decimals) + Decimal("0e-3"))
            .quantize(Decimal("1e-3"), rounding=ROUND_HALF_UP)
            .normalize()
        )
        await bs.send_message_with_intro(
            text=translate(
                tag_or_text="employee",
                domain="tip.on_success",
                lang=employee.language_code,
                amount=amount,
                symbol=tip.asset.symbol,
                sender_name=tip.sender.name,
            ),
            user_id=employee.id,
            lang=employee.language_code,
        )

    @classmethod
    def calculate_bonus(cls, tip_amount: Decimal) -> int:
        amount = tip_amount.to_integral_value(rounding=ROUND_HALF_UP)

        return next((bonus for start, end, bonus in cls.bonus_ranges if start <= amount < end), 0)
