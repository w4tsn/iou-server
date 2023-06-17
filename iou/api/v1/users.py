from typing import Annotated, List

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
    authentication: Annotated[Authentication, Depends(dependencies.get_authentication)],
    database: Annotated[IouDBInterface, Depends(dependencies.get_db)],
) -> List[UserOut]:
    return [UserOut.from_orm(user) for _, user in database.users().items()]


@router.post("", response_model=UserOut)
def create_user(
    new_user: UserIn,
    authentication: Annotated[Authentication, Depends(dependencies.get_authentication)],
    database: Annotated[IouDBInterface, Depends(dependencies.get_db)],
) -> UserOut:
    user = User(**new_user.dict())
    database.add_user(user)
    return UserOut(**user.dict())


@router.get("/{user_id}", response_model=UserOut)
def read_user(
    user_id: UserID,
    authentication: Annotated[Authentication, Depends(dependencies.get_authentication)],
    database: Annotated[IouDBInterface, Depends(dependencies.get_db)],
) -> UserOut:
    return UserOut.from_orm(utils.get_user(database, user_id))


@router.patch("/{user_id}", response_model=UserOut)
def patch_user(
    user_id: UserID,
    user_update: UserUpdate,
    authentication: Annotated[Authentication, Depends(dependencies.get_authentication)],
    database: Annotated[IouDBInterface, Depends(dependencies.get_db)],
) -> UserOut:
    return UserOut.from_orm(database.update_user(user_id, User(**user_update.dict())))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UserID,
    authentication: Annotated[Authentication, Depends(dependencies.get_authentication)],
    database: Annotated[IouDBInterface, Depends(dependencies.get_db)],
) -> None:
    database.delete_user(user_id)


@router.get("/{user_id}/groups", response_model=List[GroupOut])
def read_user_groups(
    user_id: UserID,
    authentication: Annotated[Authentication, Depends(dependencies.get_authentication)],
    database: Annotated[IouDBInterface, Depends(dependencies.get_db)],
) -> List[GroupOut]:
    return [
        GroupOut.from_orm(group) for group in utils.get_user(database, user_id).groups
    ]


@router.get("/{user_id}/balance", response_model=int)
def get_user_balance(
    user_id: UserID,
    authentication: Annotated[Authentication, Depends(dependencies.get_authentication)],
    database: Annotated[IouDBInterface, Depends(dependencies.get_db)],
) -> int:
    return utils.get_user(database, user_id).balance()
