from __future__ import annotations

from typing import Dict, List, Optional

from iou.db.db_interface import IouDBInterface
from iou.lib.group import Group, NamedGroup
from iou.lib.user import User


class MockDB(IouDBInterface):

    _users: Dict[str, User] = {}
    _groups: Dict[str, Group] = {}

    def get_users(self) -> List[User]:
        return list(self._users.values())

    def add_user(self, user: User) -> None:
        self._users[user.user_id] = user

    def get_user(self, user_id: str) -> Optional[User]:
        return self._users[user_id]

    def delete_user(self, user_id: str) -> None:
        del self._users[user_id]

    def update_user(self, user_id: str, user_update: User) -> User:
        user = self._users[user_id].copy(update=user_update.dict(exclude_unset=True))
        self._users[user_id] = user
        return user

    def add_group(self, group: NamedGroup) -> None:
        self._groups[group.group_id] = group

    def get_group(self, group_id: str) -> Optional[Group]:
        return self._groups[group_id]

    def update_group(self, group_id: str, group_update: NamedGroup) -> NamedGroup:
        group = self._groups[group_id].copy(
            update=group_update.dict(exclude_unset=True)
        )
        self._groups[group_id] = group
        return NamedGroup(**group.dict())

    def delete_group(self, group_id: str) -> None:
        del self._groups[group_id]

    def users(self) -> Dict[str, User]:
        return self._users

    def groups(self) -> Dict[str, Group]:
        return self._groups
