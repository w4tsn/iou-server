from typing import Optional

from iou.lib.id import ID
from pydantic import BaseModel


class UserID(ID):
    
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            title='User ID',
            description='ID that uniquely identifies a user'
        )

class UserBase(BaseModel):

    name : str
    email : Optional[str]

class UserIn(UserBase):

    pass

class UserUpdate(UserBase):

    name : Optional[str]
    email : Optional[str]

class UserOut(UserBase):

    user_id : UserID

