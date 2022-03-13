from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from iou.db.db_interface import IouDBInterface
from iou.lib.group import Group
from iou.lib.user import User

from .. import dependencies
from .schemas.group import GroupOut
from .schemas.user import UserID, UserIn, UserOut, UserUpdate

router = APIRouter()


@router.get("", response_model=List[UserOut])
def read_users(
    db: IouDBInterface = Depends(dependencies.get_db),
) -> List[User]:
   return db.users

@router.post("", response_model=UserOut)
def create_user(
    *,
    db: IouDBInterface = Depends(dependencies.get_db),
    new_user : UserIn
) -> User:
    user = User(**new_user.dict())
    db.add_user(user)
    return user
   
@router.get("/{user_id}", response_model=UserOut)
def read_user(
    *,
    db: IouDBInterface = Depends(dependencies.get_db),
    user_id : UserID
) -> User:
   user = db.get_user(user_id)
   if user is None:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
   return user

@router.patch("/{user_id}", response_model=UserOut)
def patch_user(
    *,
    db: IouDBInterface = Depends(dependencies.get_db),
    user_update : UserUpdate
) -> User:
    return db.update_user(user_update)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def read_user(
    *,
    db: IouDBInterface = Depends(dependencies.get_db),
    user_id : UserID
) -> None:
   db.delete_user(user_id)

@router.get("/{user_id}/groups", response_model=List[GroupOut])
def read_user_groups(
    *,
    db: IouDBInterface = Depends(dependencies.get_db),
    user_id : UserID
) -> List[Group]:
    db.get_user(user_id).groups

@router.get("/{user_id}/balance", response_model=int)
def get_user_balance(
    *,
    db: IouDBInterface = Depends(dependencies.get_db),
    user_id : UserID
) -> int:
   user = db.get_user(user_id)
   if user is None:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
   return user.balance()

