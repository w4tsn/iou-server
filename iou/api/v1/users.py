from typing import List

from fastapi import APIRouter, Depends, status

from iou.api import dependencies
from iou.api.v1 import utils
from iou.api.v1.schemas.group import GroupOut
from iou.api.v1.schemas.user import UserID, UserIn, UserOut, UserUpdate
from iou.db.db_interface import IouDBInterface
from iou.lib.group import Group
from iou.lib.user import User
from iou.security import Authentication

router = APIRouter()


@router.get("", response_model=List[UserOut])
def read_users(
    authentication: Authentication = Depends(dependencies.get_authentication),
    database: IouDBInterface = Depends(dependencies.get_db),
) -> List[UserOut]:
    return [UserOut.from_orm(user) for _, user in database.users().items()]


@router.post("", response_model=UserOut)
def create_user(
    *,
    authentication: Authentication = Depends(dependencies.get_authentication),
    database: IouDBInterface = Depends(dependencies.get_db),
    new_user: UserIn,
) -> UserOut:
    user = User(**new_user.dict())
    database.add_user(user)
    return UserOut(**user.dict())


@router.get("/{user_id}", response_model=UserOut)
def read_user(
    *,
    authentication: Authentication = Depends(dependencies.get_authentication),
    database: IouDBInterface = Depends(dependencies.get_db),
    user_id: UserID,
) -> UserOut:
    return UserOut.from_orm(utils.get_user(database, user_id))


@router.patch("/{user_id}", response_model=UserOut)
def patch_user(
    *,
    authentication: Authentication = Depends(dependencies.get_authentication),
    user_id: UserID,
    database: IouDBInterface = Depends(dependencies.get_db),
    user_update: UserUpdate,
) -> UserOut:
    return UserOut.from_orm(database.update_user(user_id, User(**user_update.dict())))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    *,
    authentication: Authentication = Depends(dependencies.get_authentication),
    database: IouDBInterface = Depends(dependencies.get_db),
    user_id: UserID,
) -> None:
    database.delete_user(user_id)


@router.get("/{user_id}/groups", response_model=List[GroupOut])
def read_user_groups(
    *,
    authentication: Authentication = Depends(dependencies.get_authentication),
    database: IouDBInterface = Depends(dependencies.get_db),
    user_id: UserID,
) -> List[GroupOut]:
    return [
        GroupOut.from_orm(group) for group in utils.get_user(database, user_id).groups
    ]


@router.get("/{user_id}/balance", response_model=int)
def get_user_balance(
    *,
    authentication: Authentication = Depends(dependencies.get_authentication),
    database: IouDBInterface = Depends(dependencies.get_db),
    user_id: UserID,
) -> int:
    return utils.get_user(database, user_id).balance()
