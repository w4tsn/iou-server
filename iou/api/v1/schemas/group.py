from typing import List, Optional

from pydantic import BaseModel

from .user import UserOut

class GroupBase(BaseModel):

    name : str

class GroupIn(GroupBase):

    pass

class GroupUpdate(GroupBase):

    name : Optional[str]

class GroupOut(GroupBase):

    group_id : str
    users : List[UserOut]
