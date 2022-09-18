from typing import Any

from sqlalchemy.ext.declarative import AbstractConcreteBase
from sqlalchemy.orm import as_declarative, declared_attr
from sqlalchemy.schema import MetaData


@as_declarative()
class Base(AbstractConcreteBase):

    id: Any
    __name__: str
    metadata: MetaData

    @classmethod
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


# import used by alembic
# pylint: disable=unused-import
from iou.db.schemas.group import Group
from iou.db.schemas.transaction import Deposit, Transaction, Withdrawal
from iou.db.schemas.user import User
