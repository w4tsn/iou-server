from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from iou.lib.split import SplitType

from .base import Base


class Transaction(Base):
    transaction_id = Column(String, primary_key=True, index=True)
    group_id = Column(String, ForeignKey("group.group_id"))
    split_type = Column(Enum(SplitType))
    deposits = relationship("Deposit", cascade="all, delete-orphan", lazy="joined")
    withdrawals = relationship(
        "Withdrawal", cascade="all, delete-orphan", lazy="joined"
    )
    date = Column(DateTime(timezone=True), server_default=func.now())


class Deposit(Base):
    deposit_id = Column(String, primary_key=True, index=True)
    transaction_id = Column(String, ForeignKey("transaction.transaction_id"))
    user_id = Column(String, ForeignKey("user.user_id"))
    amount = Column(Integer)


class Withdrawal(Base):
    withdrawal_id = Column(String, primary_key=True, index=True)
    transaction_id = Column(String, ForeignKey("transaction.transaction_id"))
    user_id = Column(String, ForeignKey("user.user_id"))
    amount = Column(Integer)
