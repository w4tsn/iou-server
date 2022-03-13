from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from .id import ID

class Group(BaseModel):

    group_id : Optional[ID] = Field(default_factory=ID.generate)
    users : List[User] = []
    transactions : List[Transaction] = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for user in self.users:
            user.add_group(self)

    def add_user(self, user : User) -> None:
        self.users.append(user)
        
    def add_user_with_backreference(self, user : User) -> None:
        self.add_user(user)
        user.add_group(self)

    def add_transaction(self, transaction : Transaction) -> None:
        assert all(user in self.users for user in transaction.users()), 'User mismatch between group and transaction'
        self.transactions.append(transaction)

    def deposits_by(self, user : User) -> List[PartialTransaction]:
        return [d for deposits in [t.deposits for t in self.transactions] for d in deposits if d.user == user]

    def withdrawals_by(self, user : User) -> List[PartialTransaction]:
        return [w for withdrawals in [t.withdrawals for t in self.transactions] for w in withdrawals if w.user == user]

    def balances(self) -> Dict[User, int]:
        return {user: self.balance_for(user) for user in self.users}

    def balance_for(self, user : User) -> int:
        return int(sum(self.deposits_by(user))) - int(sum(self.withdrawals_by(user)))

class NamedGroup(Group):

    name : str
    description : Optional[str] = None

# loading circular dependencies after everything else prevents problems with ForwardRefs introduced by pydantic
from iou.lib.transaction import *
from iou.lib.user import *

Group.update_forward_refs()
