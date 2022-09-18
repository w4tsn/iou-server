from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel

from iou.api.v1.schemas.user import UserID
from iou.lib.split import SplitType
from iou.lib.transaction import Transaction


class TransactionBase(BaseModel):

    split_type: SplitType
    date: Optional[datetime]


class TransactionIn(TransactionBase):

    deposits: Dict[UserID, int]
    split_parameters: Dict[UserID, Any]


class TransactionOut(TransactionBase):

    deposits: Dict[UserID, int]
    withdrawals: Dict[UserID, int]

    @classmethod
    def from_transaction(cls, transaction: Transaction) -> "TransactionOut":
        deposits = {
            UserID(partial_transaction.user.user_id): partial_transaction.amount
            for partial_transaction in transaction.deposits
        }
        withdrawals = {
            UserID(partial_transaction.user.user_id): partial_transaction.amount
            for partial_transaction in transaction.withdrawals
        }
        return cls(
            **transaction.dict(exclude={"deposits", "withdrawals"}),
            deposits=deposits,
            withdrawals=withdrawals
        )
