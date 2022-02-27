from __future__ import annotations
from typing import TYPE_CHECKING, List
from pydantic import BaseModel


class User(BaseModel):

    user_id : str
    name : str
    email : str
    groups : List[Group] = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for group in self.groups:
            group.add_user(self)

    def __hash__(self) -> int:
        return hash(self.user_id) ^ hash(User)
    
    def __eq__(self, other) -> bool:
        return isinstance(other, User) and self.user_id == other.user_id

    def __str__(self) -> str:
        return f'User {self.user_id}: {self.name}'
    
    def __repr__(self) -> str:
        return str(self)

    def add_group(self, group : Group) -> None:
        self.groups.append(group)

    def add_group_with_backreference(self, group : Group) -> None:
        self.add_group(group)
        group.add_user(self)

    def balance(self) -> int:
        return sum([group.balance_for(self) for group in self.groups])

# loading circular dependencies after everything else prevents problems with ForwardRefs introduced by pydantic
from iou.lib.group import *
User.update_forward_refs()