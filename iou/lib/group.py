from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from iou.lib.id import ID


class Group(BaseModel):

    group_id: ID = Field(default_factory=ID.generate)
    users: List[User] = []
    transactions: List[Transaction] = []

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for user in self.users:
            user.add_group(self)

    def add_user(self, user: User) -> None:
        self.users.append(user)

    def add_user_with_backreference(self, user: User) -> None:
        self.add_user(user)
        user.add_group(self)

    def add_transaction(self, transaction: Transaction) -> None:
        assert all(
            user in self.users for user in transaction.users()
        ), "User mismatch between group and transaction"
        self.transactions.append(transaction)

    def deposits_by(self, user: User) -> List[PartialTransaction]:
        return [
            d
            for deposits in [t.deposits for t in self.transactions]
            for d in deposits
            if d.user == user
        ]

    def withdrawals_by(self, user: User) -> List[PartialTransaction]:
        return [
            w
            for withdrawals in [t.withdrawals for t in self.transactions]
            for w in withdrawals
            if w.user == user
        ]

    def balances(self) -> Dict[User, int]:
        return {user: self.balance_for(user) for user in self.users}

    def balance_for(self, user: User) -> int:
        return PartialTransaction.reduce(
            self.deposits_by(user)
        ) - PartialTransaction.reduce(self.withdrawals_by(user))

    def transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Get a transaction from this group"""
        try:
            transaction = [
                transaction
                for transaction in self.transactions
                if transaction.transaction_id is not None
                and transaction.transaction_id == transaction_id
            ][0]
        except KeyError:
            transaction = None
        return transaction


class NamedGroup(Group):

    name: str = str(uuid.uuid4())
    description: Optional[str] = None


# loading circular dependencies after everything else prevents problems with
# ForwardRefs introduced by pydantic
from iou.lib.transaction import PartialTransaction, Transaction
from iou.lib.user import User

Group.update_forward_refs()
NamedGroup.update_forward_refs()
