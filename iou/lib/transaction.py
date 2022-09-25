from __future__ import annotations

from datetime import datetime
from functools import reduce
from typing import Any, List, Optional, Set

from pydantic import BaseModel, Field

from iou.lib.id import ID


class PartialTransaction(BaseModel):

    user: User
    amount: int

    def __init__(self, user: User, amount: int, *args: Any, **kwargs: Any) -> None:
        kwargs["user"] = user
        kwargs["amount"] = amount
        super().__init__(*args, **kwargs)

    def __int__(self) -> int:
        return self.amount

    def __add__(self, other: PartialTransaction) -> PartialTransaction:
        if self.user != other.user:
            raise ValueError("User mismatch in transaction addition")
        return PartialTransaction(self.user, self.amount + other.amount)

    @classmethod
    def reduce(cls, transactions: List[PartialTransaction]) -> int:
        """Reduce a list of partial transactions to it's integer sum"""
        return reduce(lambda total, next: next.amount + total, transactions, 0)


class Transaction(BaseModel):

    transaction_id: Optional[ID] = Field(default_factory=ID.generate)
    split_type: Optional[SplitType] = None
    deposits: List[PartialTransaction]
    withdrawals: List[PartialTransaction] = []
    date: datetime = datetime.now()

    def __init__(
        self,
        *args: Any,
        split: Optional[SplitStrategy] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        if split is not None:
            self.split_type = split.split_type
            self.withdrawals = split.compute_split()
        else:
            assert (
                self.split_type is not None and len(self.withdrawals) > 0
            ), "Either split or (split_type and withdrawals) is required."

    def users(self) -> Set[User]:
        return {pt.user for pt in self.deposits + self.withdrawals}

    class Config:
        orm_mode = True


# loading circular dependencies after everything else prevents problems with ForwardRefs introduced by pydantic
from iou.lib.split import SplitStrategy, SplitType
from iou.lib.user import User

Transaction.update_forward_refs()
PartialTransaction.update_forward_refs()
