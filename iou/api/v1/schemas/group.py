from typing import List, Optional

from pydantic import BaseModel

from iou.api.v1.schemas.user import UserOut


class GroupBase(BaseModel):
    name: Optional[str]


class GroupIn(GroupBase):
    pass


class GroupUpdate(GroupBase):
    name: Optional[str]


class GroupOut(GroupBase):
    group_id: str
    users: List[UserOut]

    class Config:
        orm_mode = True
