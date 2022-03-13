from datetime import datetime
from typing import Any, Dict, List, Optional

from iou.lib.split import SplitType
from iou.lib.transaction import PartialTransaction, Transaction
from pydantic import BaseModel, Field

from .user import UserID


class TransactionBase(BaseModel):

    split_type : SplitType
    date : Optional[datetime]

class TransactionIn(TransactionBase):

    deposits : Dict[UserID, int]
    split_parameters : Dict[UserID, Any]

class TransactionOut(TransactionBase):

    deposits : Dict[UserID, int]
    withdrawals : Dict[UserID, int]

    @classmethod
    def from_transaction(cls, transaction : Transaction):
        deposits = {partial_transaction.user.user_id: partial_transaction.amount for partial_transaction in transaction.deposits}
        withdrawals = {partial_transaction.user.user_id: partial_transaction.amount for partial_transaction in transaction.withdrawals}
        return cls(**transaction.dict(exclude={'deposits', 'withdrawals'}), deposits=deposits, withdrawals=withdrawals)
