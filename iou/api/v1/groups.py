from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from iou.db.db_interface import IouDBInterface
from iou.lib.group import Group, NamedGroup
from iou.lib.transaction import Transaction, PartialTransaction
from iou.lib.split import SplitStrategy

from .. import dependencies
from .schemas.group import GroupIn, GroupOut, GroupUpdate
from .schemas.transaction import TransactionIn, TransactionOut
from .schemas.user import UserID

router = APIRouter()


@router.get("", response_model=List[GroupOut])
def read_groups(
    db: IouDBInterface = Depends(dependencies.get_db),
) -> List[Group]:
   return db.groups

@router.post("", response_model=GroupOut)
def create_group(
    *,
    db: IouDBInterface = Depends(dependencies.get_db),
    new_group : GroupIn
) -> NamedGroup:
    group = NamedGroup(**new_group.dict())
    db.add_group(group)
    return group

@router.get('/{group_id}', response_model=GroupOut)
def read_group(
    *,
    db: IouDBInterface = Depends(dependencies.get_db),
    group_id : str
) -> Group:
    db.get_group(group_id)

@router.patch("/{group_id}", response_model=GroupOut)
def patch_group(
    *,
    db: IouDBInterface = Depends(dependencies.get_db),
    group_update : GroupUpdate
) -> Group:
    return db.update_group(group_update)

@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def read_group(
    *,
    db: IouDBInterface = Depends(dependencies.get_db),
    group_id : str
) -> None:
   db.delete_group(group_id)

@router.put('/{group_id}/addUser/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def add_user(
    *,
    db: IouDBInterface = Depends(dependencies.get_db),
    group_id : str,
    user_id : UserID
) -> None:
    db.get_group(group_id).add_user(db.get_user(user_id))

@router.get("/{group_id}/transactions", response_model=List[TransactionOut])
def read_transactions(
    *,
    db: IouDBInterface = Depends(dependencies.get_db),
    group_id: str
) -> List[Transaction]:
    return db.get_group(group_id).transactions

@router.post("/{group_id}/transactions", response_model=TransactionOut)
def create_transaction(
    *,
    db: IouDBInterface = Depends(dependencies.get_db),
    group_id: str,
    transaction_in : TransactionIn
) -> Transaction:
    deposits = [PartialTransaction(db.get_user(user_id), amount) for user_id, amount in transaction_in.deposits.items()]
    split_parameters = {db.get_user(user_id): amount for user_id, amount in transaction_in.split_parameters.items()}
    split_strategy = SplitStrategy.create(transaction_in.split_type, split_parameters, deposits)
    transaction = Transaction(**transaction_in.dict(exclude={'deposits', 'split_parameters'}), split=split_strategy, deposits=deposits)
    db.get_group(group_id).add_transaction(transaction)
    return TransactionOut.from_transaction(transaction)

@router.get("/{group_id}/transactions/{transaction_id}", response_model=TransactionOut)
def read_transaction(
    *,
    db: IouDBInterface = Depends(dependencies.get_db),
    group_id: str,
    transaction_id : str
) -> Transaction:
    return db.get_group(group_id).transactions()


@router.get("/{group_id}/balances", response_model=Dict[UserID, int])
def read_group_balances(
    *,
    db: IouDBInterface = Depends(dependencies.get_db),
    group_id: str
) -> Dict[UserID, int]:
    return {user.user_id: balance for user, balance in db.get_group(group_id).balances().items()}

@router.get("/{group_id}/balances/{user_id}", response_model=int)
def read_group_user_balance(
    *,
    db: IouDBInterface = Depends(dependencies.get_db),
    group_id: str,
    user_id: UserID
) -> int:
    return db.get_group(group_id).balance_for(db.get_user(user_id))
