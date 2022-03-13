from __future__ import annotations

import uuid
from typing import Dict, List, Optional

from pydantic import BaseModel

from ..lib.group import Group, NamedGroup
from ..lib.user import User
from .db_interface import IouDBInterface


class MockDB(IouDBInterface):

    users : Dict[str, User] = {}
    groups : Dict[str, Group] = {}

    def get_users(self) -> List[User]:
        return list(self.users.values())

    def add_user(self, user : User) -> None:
        self.users[user.user_id] = user

    def get_user(self, user_id : str) -> Optional[User]:
        return self.users[user_id]
        
    def delete_user(self, user_id : str) -> None:
        self.users[user_id] = None

    def update_user(self, user_id : str, user_update : User) -> User:
        user = self.users[user_id].copy(update=user_update.dict(exclude_unset=True))
        self.users[user_id] = user
        return user

    def add_group(self, group : NamedGroup) -> None:
        self.groups[group.group_id] = group

    def get_group(self, group_id : str) -> Optional[Group]:
        return self.groups[group_id]

    def update_group(self, group_id : str, group_update : NamedGroup) -> NamedGroup:
        group = self.groups[group_id].copy(update=group_update.dict(exclude_unset=True))
        self.groups[group_id] = group
        return group

    def delete_group(self, group_id : str) -> None:
        self.groups[group_id] = None
