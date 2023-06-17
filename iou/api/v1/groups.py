from typing import Dict, List

from fastapi import APIRouter, Depends, status

from iou.api import dependencies
from iou.api.v1 import utils
from iou.api.v1.schemas.group import GroupIn, GroupOut, GroupUpdate
from iou.api.v1.schemas.transaction import TransactionIn, TransactionOut
from iou.api.v1.schemas.user import UserID
from iou.db.db_interface import IouDBInterface
from iou.lib.group import Group, NamedGroup
from iou.lib.split import SplitStrategy
from iou.lib.transaction import PartialTransaction, Transaction
from iou.security import Authentication

router = APIRouter()


@router.get("", response_model=List[GroupOut])
def read_groups(
    authentication: Authentication = Depends(dependencies.get_authentication),
    database: IouDBInterface = Depends(dependencies.get_db),
) -> List[GroupOut]:
    return [GroupOut.from_orm(group) for _, group in database.groups().items()]


@router.post("", response_model=GroupOut)
def create_group(
    *,
    authentication: Authentication = Depends(dependencies.get_authentication),
    database: IouDBInterface = Depends(dependencies.get_db),
    new_group: GroupIn,
) -> GroupOut:
    group = NamedGroup(**new_group.dict())
    database.add_group(group)
    return GroupOut(**group.dict())


@router.get("/{group_id}", response_model=GroupOut)
def read_group(
    *,
    authentication: Authentication = Depends(dependencies.get_authentication),
    database: IouDBInterface = Depends(dependencies.get_db),
    group_id: str,
) -> GroupOut:
    return GroupOut.from_orm(utils.get_group(database, group_id))


@router.patch("/{group_id}", response_model=GroupOut)
def patch_group(
    *,
    authentication: Authentication = Depends(dependencies.get_authentication),
    group_id: str,
    database: IouDBInterface = Depends(dependencies.get_db),
    group_update: GroupUpdate,
) -> GroupOut:
    return GroupOut.from_orm(
        database.update_group(group_id, NamedGroup(**group_update.dict()))
    )


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(
    *,
    authentication: Authentication = Depends(dependencies.get_authentication),
    database: IouDBInterface = Depends(dependencies.get_db),
    group_id: str,
) -> None:
    database.delete_group(group_id)


@router.put("/{group_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def add_user(
    *,
    authentication: Authentication = Depends(dependencies.get_authentication),
    database: IouDBInterface = Depends(dependencies.get_db),
    group_id: str,
    user_id: UserID,
) -> None:
    return utils.get_group(database, group_id).add_user(
        utils.get_user(database, user_id)
    )


@router.get("/{group_id}/transactions", response_model=List[TransactionOut])
def read_transactions(
    *,
    authentication: Authentication = Depends(dependencies.get_authentication),
    database: IouDBInterface = Depends(dependencies.get_db),
    group_id: str,
) -> List[TransactionOut]:
    return [
        TransactionOut.from_orm(
            transaction
            for transaction in utils.get_group(database, group_id).transactions
        )
    ]


@router.post("/{group_id}/transactions", response_model=TransactionOut)
def create_transaction(
    *,
    authentication: Authentication = Depends(dependencies.get_authentication),
    database: IouDBInterface = Depends(dependencies.get_db),
    group_id: str,
    transaction_in: TransactionIn,
) -> TransactionOut:
    deposits = [
        PartialTransaction(utils.get_user(database, user_id), amount)
        for user_id, amount in transaction_in.deposits.items()
    ]
    split_parameters = {
        utils.get_user(database, user_id): amount
        for user_id, amount in transaction_in.split_parameters.items()
    }
    split_strategy = SplitStrategy.create(
        transaction_in.split_type, split_parameters, deposits
    )
    transaction = Transaction(
        **transaction_in.dict(exclude={"deposits", "split_parameters"}),
        split=split_strategy,
        deposits=deposits,
    )
    utils.get_group(database, group_id).add_transaction(transaction)
    return TransactionOut.from_transaction(transaction)


@router.get("/{group_id}/transactions/{transaction_id}", response_model=TransactionOut)
def read_transaction(
    *,
    authentication: Authentication = Depends(dependencies.get_authentication),
    transaction_id: str,
    database: IouDBInterface = Depends(dependencies.get_db),
    group_id: str,
) -> TransactionOut:
    return TransactionOut.from_transaction(
        utils.get_transaction(database, group_id, transaction_id)
    )


@router.get("/{group_id}/balances", response_model=Dict[UserID, int])
def read_group_balances(
    *,
    authentication: Authentication = Depends(dependencies.get_authentication),
    database: IouDBInterface = Depends(dependencies.get_db),
    group_id: str,
) -> Dict[UserID, int]:
    return {
        UserID(user.user_id): balance
        for user, balance in utils.get_group(database, group_id).balances().items()
    }


@router.get("/{group_id}/balances/{user_id}", response_model=int)
def read_group_user_balance(
    *,
    authentication: Authentication = Depends(dependencies.get_authentication),
    database: IouDBInterface = Depends(dependencies.get_db),
    group_id: str,
    user_id: UserID,
) -> int:
    return utils.get_group(database, group_id).balance_for(
        utils.get_user(database, user_id)
    )
