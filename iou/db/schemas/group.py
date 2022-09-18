from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import relationship

from .base import Base

group_membership_table = Table(
    "group_membership",
    Base.metadata,
    Column("group_id", ForeignKey("group.group_id")),
    Column("user_id", ForeignKey("user.user_id")),
)


class Group(Base):

    group_id = Column(String, primary_key=True, index=True)
    users = relationship(
        "User", secondary=group_membership_table, back_populates="groups"
    )
    transactions = relationship("Transaction")
