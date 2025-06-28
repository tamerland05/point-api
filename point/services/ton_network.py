from pytoniq_core import Address, Cell, begin_cell
from tonutils.client import Client
from tonutils.jetton import JettonWalletStandard
from tonutils.jetton.contract.standard.op_codes import JETTON_TRANSFER_OPCODE
from tonutils.utils import boc_to_base64_string
from tonutils.wallet.op_codes import TEXT_COMMENT_OPCODE

from point.config import settings
from point.entity_types import TonAddress, PointBlockchainHash
from point.view import JettonWalletOut, TransactionDbOut, BlockchainTransactionOut, GetTrxByMsgCriteria


def create_text_cell(payload: str) -> Cell:
    return (
        begin_cell()
        .store_uint(TEXT_COMMENT_OPCODE, 32)
        .store_snake_string(payload)
        .end_cell()
    )


def check_transaction(
        transaction: TransactionDbOut,
        blockchain_transaction: BlockchainTransactionOut,
) -> bool:
    return (
            blockchain_transaction.description.action.success and
            blockchain_transaction.account == transaction.to and
            blockchain_transaction.in_msg.source == transaction.sender and
            blockchain_transaction.in_msg.destination == transaction.to and
            blockchain_transaction.in_msg.value == transaction.value and
            not blockchain_transaction.in_msg.bounced and
            blockchain_transaction.in_msg.opcode == transaction.opcode and
            blockchain_transaction.now >= transaction.now
    )


class TonNetworkService(Client):
    JETTON_TRANSFER_OPCODE = JETTON_TRANSFER_OPCODE

    def __init__(self):
        super().__init__(
            base_url=settings.ton_indexer_url,
            headers={"X-Api-Key": settings.ton_indexer_api_key},
            rps=settings.ton_indexer_rps,
        )

    async def get_jetton(self, jetton_master: TonAddress, owner_address: TonAddress) -> JettonWalletOut:
        method = "/jetton/wallets"

        resp = await self._get(method=method, params={
            "jetton_address": jetton_master,
            "owner_address": owner_address,
        })

        jetton_wallet = resp["jetton_wallets"][0]
        return JettonWalletOut.model_validate(jetton_wallet)

    async def _get_transactions_by_message(
            self,
            criteria: GetTrxByMsgCriteria,
    ) -> list[BlockchainTransactionOut]:
        method = "/transactionsByMessage"
        resp = await self._get(method=method, params=criteria.model_dump(mode="json", exclude_none=True))
        return [BlockchainTransactionOut.model_validate(t) for t in resp["transactions"]]

    @staticmethod
    def create_jetton_transfer(
            sender_address: TonAddress,
            sender_jetton_wallet_address: TonAddress,
            destination_address: TonAddress,
            jetton_amount: int,
            payload: str
    ) -> TransactionDbOut:
        body = JettonWalletStandard.build_transfer_body(
            recipient_address=Address(destination_address),
            response_address=Address(sender_address),
            jetton_amount=jetton_amount,
            forward_payload=create_text_cell(payload)
        )

        return TransactionDbOut(
            to=sender_jetton_wallet_address,
            value=settings.jetton_transfer_amount,
            body=boc_to_base64_string(body.to_boc()),
            sender=sender_address,
            body_hash=PointBlockchainHash(root=boc_to_base64_string(body.hash)),
            out_message_opcode=0,
        )

    @staticmethod
    def create_ton_transfer(
            sender_address: TonAddress,
            destination_address: TonAddress,
            ton_amount: int,
            payload: str
    ) -> TransactionDbOut:
        body = create_text_cell(payload)

        return TransactionDbOut(
            to=destination_address,
            value=ton_amount,
            body=boc_to_base64_string(body.to_boc()),
            sender=sender_address,
            body_hash=PointBlockchainHash(root=boc_to_base64_string(body.hash)),
            out_message_opcode=JETTON_TRANSFER_OPCODE,
        )

    @staticmethod
    def _find_transaction(
            transaction: TransactionDbOut,
            blockchain_transactions: list[BlockchainTransactionOut]
    ) -> BlockchainTransactionOut | None:
        for t in blockchain_transactions:
            if check_transaction(transaction=transaction, blockchain_transaction=t):
                return t
        return None

    async def _check_jetton_transfer(self, transaction: BlockchainTransactionOut) -> bool:
        if len(transaction.out_msgs) != 1:
            return False

        supposed_internal_transactions = await self._get_transactions_by_message(
            criteria=GetTrxByMsgCriteria(msg_hash=transaction.out_msgs[0].hash),
        )
        for t in supposed_internal_transactions:
            if t.in_msg.source == transaction.account and t.description.action.success:
                return True

        return False

    async def is_transaction_completed(self, transaction: TransactionDbOut) -> bool:
        supposed_transactions = await self._get_transactions_by_message(
            criteria=GetTrxByMsgCriteria(
                body_hash=transaction.body_hash,
                opcode=transaction.out_message_opcode,
            )
        )

        blockchain_transaction = self._find_transaction(
            transaction=transaction,
            blockchain_transactions=supposed_transactions
        )

        if blockchain_transaction is None:
            return False

        match blockchain_transaction.in_msg.opcode:
            case self.JETTON_TRANSFER_OPCODE:
                return await self._check_jetton_transfer(transaction=blockchain_transaction)
            case _:
                return True


tns = TonNetworkService()
