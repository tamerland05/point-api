import asyncio
import datetime
import logging
import uuid

from point.config import settings
from point.controllers.base import BaseController
from point.controllers import EstablishmentController, UserController
from point.entity_types import TonAddress, RecipientType, TipStatus
from point.errors import ErrorCode, APIException
from point.models import Tip
from point.services import tns
from point.view import CheckoutTipIn, TransactionDbOut

from .asset import AssetController


class TipController(BaseController[Tip]):
    model = Tip
    error_code: ErrorCode = ErrorCode.TIP_NOT_FOUND

    @classmethod
    async def create_tip(cls, checkout_in: CheckoutTipIn, sender_id: int) -> model:
        sender, asset, recipient = await asyncio.gather(
            UserController.get_user(user_id=sender_id),
            AssetController.get_asset(asset_id=checkout_in.asset_id),
            EstablishmentController.get_establishment(establishment_id=checkout_in.recipient_id)
            if checkout_in.recipient_type == RecipientType.establishment
            else UserController.get_by_employee(employee_id=checkout_in.recipient_id)
        )
        if sender.wallet is None:
            raise APIException(ErrorCode.USER_HAVE_NOT_WALLET)

        tip_id = uuid.uuid4()
        asset_amount = int(checkout_in.amount * (10 ** asset.decimals))
        fee = asset_amount // 10
        fix_fee = 0
        payload = str(tip_id)

        if asset.symbol == "TON":
            fee_transaction, tip_transaction = cls._create_ton_tip(
                supposed_fee=fee,
                payload=payload,
                destination_address=recipient.wallet,
                asset_amount=asset_amount,
                sender_address=sender.wallet,
            )
        else:
            sender_jetton_wallet = await tns.get_jetton(
                jetton_master=asset.address,
                owner_address=sender.wallet,
            )
            fee_transaction, tip_transaction, fix_fee = cls._create_jetton_tip(
                supposed_fee=fee,
                payload=payload,
                sender_address=sender.wallet,
                sender_jetton_wallet_address=sender_jetton_wallet.address,
                destination_address=recipient.wallet,
                asset_amount=asset_amount,
                asset_ton_price=asset.ton_price,
            )

        tip = await cls.model.create(
            id=tip_id,
            sender_id=sender_id,
            employee_id=checkout_in.recipient_id if checkout_in.recipient_type == RecipientType.employee else None,
            establishment_id=checkout_in.recipient_id if checkout_in.recipient_type != RecipientType.employee else None,
            asset=asset,
            fee_transaction=fee_transaction.model_dump(mode="json"),
            tip_transaction=tip_transaction.model_dump(mode="json"),
            expired_at=(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)),
            amount=checkout_in.amount,
            tips_left_amount=asset_amount * asset.ton_price + fix_fee
        )

        return tip

    @staticmethod
    def _create_ton_tip(
            sender_address: TonAddress,
            supposed_fee: int,
            payload: str,
            destination_address: TonAddress,
            asset_amount: int,
    ):
        fee_transaction = tns.create_ton_transfer(
            sender_address=sender_address,
            destination_address=settings.point_wallet,
            ton_amount=supposed_fee,
            payload=payload,
        )

        tip_transaction = tns.create_ton_transfer(
            sender_address=sender_address,
            destination_address=destination_address,
            ton_amount=asset_amount,
            payload=payload,
        )

        return fee_transaction, tip_transaction

    @staticmethod
    def _create_jetton_tip(
            supposed_fee: int,
            payload: str,
            sender_address: TonAddress,
            sender_jetton_wallet_address: TonAddress,
            destination_address: TonAddress,
            asset_amount: int,
            asset_ton_price: int
    ):
        if supposed_fee * asset_ton_price < settings.fix_fee:
            fee_transaction = tns.create_ton_transfer(
                destination_address=settings.point_wallet,
                ton_amount=settings.fix_fee,
                payload=payload,
            )
            supposed_fee = 0
        else:
            fee_transaction = tns.create_jetton_transfer(
                sender_jetton_wallet_address=sender_jetton_wallet_address,
                destination_address=settings.point_wallet,
                response_address=sender_address,
                jetton_amount=supposed_fee,
                payload=payload,
            )

        tip_transaction = tns.create_jetton_transfer(
            sender_jetton_wallet_address=sender_jetton_wallet_address,
            destination_address=destination_address,
            response_address=sender_address,
            jetton_amount=asset_amount - supposed_fee,
            payload=payload,
        )

        return fee_transaction, tip_transaction, (0 if supposed_fee == 0 else settings.fix_fee)

    @classmethod
    async def pooling_tips(cls):
        tips = await cls.filter(status=TipStatus.created)

        for t in tips:
            try:
                await cls._check_tip_completion(tip=t)
            except Exception as e:
                logging.exception(e)
                logging.error(f'error while pooling tip {t.id}')

    @classmethod
    async def _check_tip_completion(cls, tip: Tip) -> None:
        is_completed = (
                tns.is_transaction_completed(
                    transaction=TransactionDbOut.model_validate(tip.fee_transaction),
                ) and
                tns.is_transaction_completed(
                    transaction=TransactionDbOut.model_validate(tip.tip_transaction),
                )
        )

        if is_completed:
            tip.status = TipStatus.accepted
            # todo: actions on completion with sender and receiver
        elif tip.expired_at >= datetime.datetime.now(datetime.timezone.utc):
            tip.status = TipStatus.failed
        else:
            return

        await tip.save(update_fields=['status'])
