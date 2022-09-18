from __future__ import annotations

import functools
from abc import ABC, abstractmethod
from enum import Enum
from typing import ClassVar, Dict, List, Set, Type

from pydantic import BaseModel, validator


class SplitType(str, Enum):

    BY_SHARE = "by_share"
    BY_PERCENTAGE = "by_percentage"
    BY_ADJUSTMENT = "by_adjustment"
    EQUAL = "equal"
    UNEQUAL = "unequal"


class SplitStrategy(BaseModel, ABC):

    split_type: ClassVar[SplitType]
    split_parameters: Dict[User, int]
    deposits: List[PartialTransaction]

    @abstractmethod
    def compute_split(self) -> List[PartialTransaction]:
        pass

    @classmethod
    def create(
        cls,
        split_type: SplitType,
        split_parameters: Dict[User, int],
        deposits: List[PartialTransaction],
    ) -> SplitStrategy:
        return next(sc for sc in cls.all_subclasses() if sc.split_type == split_type)(
            split_parameters=split_parameters, deposits=deposits
        )

    @classmethod
    def all_subclasses(cls: Type[SplitStrategy]) -> Set[Type[SplitStrategy]]:
        return set(cls.__subclasses__()).union(
            [s for c in cls.__subclasses__() for s in c.all_subclasses()]
        )

    def total(self) -> int:
        return functools.reduce(lambda s, d: s + d.amount, self.deposits, 0)


class EqualSplitStrategy(SplitStrategy):

    split_type: ClassVar[SplitType] = SplitType.EQUAL

    def withdrawers(self) -> List[User]:
        return list(self.split_parameters.keys())

    def compute_split(self) -> List[PartialTransaction]:
        share = self.total() / len(self.withdrawers())
        return [
            PartialTransaction(withdrawer, round(share))
            for withdrawer in self.withdrawers()
        ]


class UnequalSplitStrategy(SplitStrategy):

    split_type: ClassVar[SplitType] = SplitType.UNEQUAL

    def compute_split(self) -> List[PartialTransaction]:
        return [PartialTransaction(**item) for item in self.split_parameters.items()]


class ByShareSplitStrategy(SplitStrategy):

    split_type: ClassVar[SplitType] = SplitType.BY_SHARE

    def compute_split(self) -> List[PartialTransaction]:
        total_shares = sum(self.split_parameters.values())
        total = self.total()
        return [
            PartialTransaction(*item)
            for item in {
                withdrawer: round(share / total_shares * total)
                for withdrawer, share in self.split_parameters.items()
            }.items()
        ]


class ByPercentageSplitStrategy(ByShareSplitStrategy):

    split_type: ClassVar[SplitType] = SplitType.BY_PERCENTAGE

    @classmethod
    @validator("split_parameters")
    def _share_total(cls, shares_dict: Dict[User, int]) -> Dict[User, int]:
        if sum(shares_dict.values()) != 100:
            raise ValueError("Percentage shares must add up to 100")
        return shares_dict


class ByAdjustmentSplitStrategy(SplitStrategy):

    split_type: ClassVar[SplitType] = SplitType.BY_ADJUSTMENT

    def compute_split(self) -> List[PartialTransaction]:
        equal_amount = round(
            (self.total() - sum(self.split_parameters.values()))
            / len(self.split_parameters.items())
        )
        return [
            PartialTransaction(withdrawer, amount)
            for withdrawer, amount in {
                withdrawer: adjustment + equal_amount
                for withdrawer, adjustment in self.split_parameters.items()
            }
        ]


# loading circular dependencies after everything else prevents problems with ForwardRefs introduced by pydantic
from iou.lib.transaction import PartialTransaction
from iou.lib.user import User

EqualSplitStrategy.update_forward_refs()
UnequalSplitStrategy.update_forward_refs()
ByShareSplitStrategy.update_forward_refs()
ByPercentageSplitStrategy.update_forward_refs()
ByAdjustmentSplitStrategy.update_forward_refs()
