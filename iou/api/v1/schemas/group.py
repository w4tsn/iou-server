from typing import List

from pydantic import BaseModel

from iou.api.v1.schemas.user import UserOut


class GroupBase(BaseModel):
    name: str | None


class GroupIn(GroupBase):
    pass


class GroupUpdate(GroupBase):
    name: str | None


class GroupOut(GroupBase):
    group_id: str
    users: List[UserOut]

    class Config:
        orm_mode = True
