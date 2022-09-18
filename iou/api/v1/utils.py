from fastapi import HTTPException, status

from iou.db.db_interface import IouDBInterface
from iou.lib.group import Group
from iou.lib.transaction import Transaction
from iou.lib.user import User


def get_user(database: IouDBInterface, user_id: str) -> User:
    """Get user from database and raise HTTPException if not found."""
    user = database.get_user(user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="user not found")
    return user


def get_group(database: IouDBInterface, group_id: str) -> Group:
    """Get group from database and raise HTTPException if not found."""
    group = database.get_group(group_id)
    if group is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="group not found")
    return group


def get_transaction(
    database: IouDBInterface, group_id: str, transaction_id: str
) -> Transaction:
    """Get transaction of group from database and raise HTTPException if not found."""
    transaction = get_group(database, group_id).transaction(transaction_id)
    if transaction is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="transaction not found")
    return transaction
