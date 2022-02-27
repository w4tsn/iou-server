from __future__ import annotations

import functools
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, validator


class SplitType(str,Enum):

    BY_SHARE = 'by_share'
    BY_PERCENTAGE = 'by_percentage'
    BY_ADJUSTMENT = 'by_adjustment'
    EQUAL = 'equal'
    UNEQUAL = 'unequal'

class SplitStrategy(BaseModel):
        
    split_type : SplitType

    deposits : List[PartialTransaction]

    @classmethod
    def compute_split(self) -> List[PartialTransaction]:
        pass

    def total(self) -> int:
        return functools.reduce(lambda s, d: s + d.amount, self.deposits, 0)

class EqualSplitStrategy(SplitStrategy):

    split_type = SplitType.EQUAL

    withdrawers : List[User]

    def compute_split(self) :
        share = self.total() / len(self.withdrawers)
        return [PartialTransaction(withdrawer, share) for withdrawer in self.withdrawers]

class UnequalSplitStrategy(SplitStrategy):

    split_type = SplitType.UNEQUAL

    withdrawal_amounts : Dict[User, int]
 
    def compute_split(self) -> List[PartialTransaction]:
        return [PartialTransaction(**item) for item in self.withdrawal_amounts.items()]


class ByShareSplitStrategy(SplitStrategy):

    split_type = SplitType.BY_SHARE

    shares : Dict[User, int]

    def compute_split(self) -> List[PartialTransaction]:
        total_shares = sum(self.shares.values())
        total = self.total()
        return [PartialTransaction(*item) for item in {withdrawer: round(share / total_shares * total) for withdrawer, share in self.shares.items()}.items()]

class ByPercentageSplitStrategy(ByShareSplitStrategy):

    split_type = SplitType.BY_PERCENTAGE

    @validator('shares')
    def _share_total(cls, shares_dict : Dict[User, int]) -> Dict[User, int]:
        if sum(shares_dict.values()) != 100:
            raise ValueError('Percentage shares must add up to 100')
        return shares_dict

class ByAdjustmentSplitStrategy(SplitStrategy):

    split_type = SplitType.BY_ADJUSTMENT

    adjustments : Dict[User, int]

    def compute_split(self) -> List[PartialTransaction]:
        equal_amount = round((self.total() - sum(self.adjustments.values())) / len(self.adjustments.items()))
        return [PartialTransaction(withdrawer, amount) for withdrawer, amount in {withdrawer: adjustment + equal_amount for withdrawer, adjustment in self.adjustments.items()}]


# loading circular dependencies after everything else prevents problems with ForwardRefs introduced by pydantic
from iou.lib.user import User
from iou.lib.transaction import PartialTransaction

EqualSplitStrategy.update_forward_refs()
UnequalSplitStrategy.update_forward_refs()
ByShareSplitStrategy.update_forward_refs()
ByPercentageSplitStrategy.update_forward_refs()
ByAdjustmentSplitStrategy.update_forward_refs()
