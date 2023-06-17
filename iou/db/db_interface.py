from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from pydantic import BaseModel

from iou.lib.group import Group, NamedGroup
from iou.lib.user import User

logger = logging.getLogger(__name__)


class IouDBInterface(BaseModel, ABC):
    _instance: Optional[IouDBInterface] = None

    @classmethod
    def instance(cls) -> "IouDBInterface":
        if cls._instance is None:
            logger.debug("Creating DB singleton")
            cls._instance = cls()
        return cls._instance

    @abstractmethod
    def get_users(self) -> List[User]:
        pass

    @abstractmethod
    def add_user(self, user: User) -> None:
        pass

    @abstractmethod
    def get_user(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    def update_user(self, user_id: str, user_update: User) -> User:
        pass

    @abstractmethod
    def delete_user(self, user_id: str) -> None:
        pass

    @abstractmethod
    def add_group(self, group: NamedGroup) -> None:
        pass

    @abstractmethod
    def get_group(self, group_id: str) -> NamedGroup | Group | None:
        pass

    @abstractmethod
    def update_group(self, group_id: str, group_update: NamedGroup) -> NamedGroup:
        pass

    @abstractmethod
    def delete_group(self, group_id: str) -> None:
        pass

    @abstractmethod
    def users(self) -> Dict[str, User]:
        pass

    @abstractmethod
    def groups(self) -> Dict[str, NamedGroup | Group | None]:
        pass
