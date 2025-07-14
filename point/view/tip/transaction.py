import time

from pydantic import Field

from point.entity_types import TonAddress, PointBlockchainHash
from point.view import PointBase


class TransactionOut(PointBase):
    to: TonAddress
    value: int
    body: str


class TransactionDbOut(TransactionOut):
    sender: TonAddress
    body_hash: PointBlockchainHash
    out_message_opcode: int
    now: int = Field(default_factory=lambda: int(time.time()))


class GetTrxByMsgCriteria(PointBase):
    msg_hash: PointBlockchainHash | None = None
    body_hash: PointBlockchainHash | None = None
    opcode: int | None = None
    direction: str = "in"
    limit: int = 1000


class BlockchainTransactionDescriptionAction(PointBase):
    success: bool
    valid: bool


class BlockchainTransactionDescriptionComputePh(PointBase):
    skipped: bool
    reason: str | None = Field(default=None)


class BlockchainTransactionDescription(PointBase):
    action: BlockchainTransactionDescriptionAction | None = Field(default=None)
    compute_ph: BlockchainTransactionDescriptionComputePh


class BlockchainTransactionMsg(PointBase):
    hash: PointBlockchainHash
    source: TonAddress
    destination: TonAddress
    value: int
    opcode: str
    bounced: bool


class BlockchainTransactionOut(PointBase):
    account: TonAddress
    now: int = Field(ge=0)
    description: BlockchainTransactionDescription
    in_msg: BlockchainTransactionMsg
    out_msgs: list[BlockchainTransactionMsg]

    def equal_to(self, db_trx: TransactionDbOut) -> bool:
        return (
                (self.description.action is None and
                 db_trx.out_message_opcode == 0 and
                 self.description.compute_ph.reason == "no_state" or
                 self.description.action is not None and
                 self.description.action.success) and
                self.account == db_trx.to and
                self.in_msg.source == db_trx.sender and
                self.in_msg.destination == db_trx.to and
                self.in_msg.value == db_trx.value and
                not self.in_msg.bounced and
                int(self.in_msg.opcode, 16) == db_trx.out_message_opcode and
                self.now >= db_trx.now
        )
