from typing import Any

from pydantic import BaseModel

from iou.lib.id import ID


class UserID(ID):
    @classmethod
    def __modify_schema__(cls, field_schema: Any) -> None:
        field_schema.update(
            title="User ID", description="ID that uniquely identifies a user"
        )


class UserBase(BaseModel):
    name: str | None
    email: str | None


class UserIn(UserBase):
    pass


class UserUpdate(UserBase):
    name: str | None
    email: str | None


class UserOut(UserBase):
    user_id: UserID

    class Config:
        orm_mode = True
