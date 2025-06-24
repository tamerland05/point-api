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


class BlockchainTransactionDescription(PointBase):
    action: BlockchainTransactionDescriptionAction


class BlockchainTransactionMsg(PointBase):
    hash: PointBlockchainHash
    source: TonAddress
    destination: TonAddress
    value: int
    opcode: int
    bounced: bool


class BlockchainTransactionOut(PointBase):
    account: TonAddress
    now: int = Field(ge=0)
    description: BlockchainTransactionDescription
    in_msg: BlockchainTransactionMsg
    out_msgs: list[BlockchainTransactionMsg]

