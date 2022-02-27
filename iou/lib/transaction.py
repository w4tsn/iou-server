from __future__ import annotations

import functools
from datetime import datetime
from enum import Enum
from typing import Dict, List, Set, Optional

from pydantic import BaseModel

class PartialTransaction(BaseModel):

    user : User
    amount : int

    def __init__(self, user : User, amount : int, *args, **kwargs):
        kwargs['user'] = user
        kwargs['amount'] = amount
        super().__init__(*args, **kwargs)

    def __int__(self) -> int:
        return self.amount

    def __add__(self, other) -> PartialTransaction:
        if self.user != other.user:
            raise ValueError('User mismatch in transaction addition')
        return PartialTransaction(self.user, self.amount + other.amount)
    
    def __radd__(self, other) -> PartialTransaction:
        return PartialTransaction(self.user, int(self.amount + other))

class Transaction(BaseModel):

    split_type : Optional[SplitType] = None
    deposits : List[PartialTransaction]
    withdrawals : Optional[List[PartialTransaction]] = None
    date : datetime = datetime.now()

    def __init__(self, *args, split : Optional[SplitStrategy] = None, **kwargs):
        super().__init__(*args, **kwargs)
        if split is not None:
            self.split_type = split.split_type
            self.withdrawals = split.compute_split()
        else:
            assert self.split_type is not None and self.withdrawals is not None, 'Either split or (split_type and withdrawals) is required.'


    def users(self) -> Set[User]:
        return {pt.user for pt in self.deposits + self.withdrawals}

# loading circular dependencies after everything else prevents problems with ForwardRefs introduced by pydantic
from iou.lib.split import SplitType, SplitStrategy
from iou.lib.user import User

Transaction.update_forward_refs()
PartialTransaction.update_forward_refs()
