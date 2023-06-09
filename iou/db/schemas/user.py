from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from .base import Base
from .group import group_membership_table


class User(Base):
    user_id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    groups = relationship(
        "Group", secondary=group_membership_table, back_populates="users", lazy="joined"
    )
