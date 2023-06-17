import logging
from contextlib import contextmanager
from timeit import default_timer as timer
from types import TracebackType
from typing import Dict, Generator, List, Optional

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import (
    ArgumentError,
    DBAPIError,
    InvalidRequestError,
    ProgrammingError,
    SQLAlchemyError,
)
from sqlalchemy.orm import Session

from iou.config import settings
from iou.db.db_interface import IouDBInterface
from iou.db.schemas.base import Base
from iou.db.schemas.group import Group as GroupSchema
from iou.db.schemas.transaction import Transaction as TransactionSchema
from iou.db.schemas.user import User as UserSchema
from iou.lib.group import Group, NamedGroup
from iou.lib.user import User

logger = logging.getLogger(__name__)


def engine_builder(uri: str = settings.IOU_DATABASE_SQLALCHEMY_URL) -> Engine:
    try:
        if "sqlite://" in uri:
            engine = create_engine(
                uri,
                connect_args={"check_same_thread": False},
            )
        elif "postgresql://" in uri:
            engine = create_engine(uri, pool_size=20)
        else:
            engine = create_engine(uri)
        logger.info("Created engine and database connection pool")
        return engine
    except SQLAlchemyError as init_error:
        logger.fatal("Error creating database pool: %s", init_error)
        raise init_error


@contextmanager
def http_context(sqlalchemy_session: Session) -> Generator[Session, None, None]:
    """
    Wrap the database context into an http context and handle db errors
    as HTTP errors if applicable.
    """
    try:
        yield sqlalchemy_session
    except (ArgumentError, InvalidRequestError) as error:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from error
    except ProgrammingError as error:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, str(error)
        ) from error
    except DBAPIError as error:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, str(error)
        ) from error


class SqlDb(IouDBInterface):
    engine: Engine | None
    session: Session | None

    def __init__(self, engine: Engine = engine_builder()) -> None:
        super().__init__()
        self.engine: Engine = engine
        self.session: Session | None = None

    def __enter__(self) -> "SqlDb":
        self.session = Session(self.engine)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self.session is not None:
            self.session.close()

    @contextmanager
    def connection(self) -> Generator[Session, None, None]:
        """Invoke a connection context manager"""
        with Session(self.engine, expire_on_commit=False) as session:
            logger.debug("Entering database session manager")
            begin_time = timer()
            try:
                yield session
            except (ArgumentError, InvalidRequestError) as error:
                logger.warning(
                    "DB transaction failed. SQLAlchemy client error: %s. Rolling back.",
                    error,
                )
                session.rollback()
                raise error
            except ProgrammingError as error:
                logger.warning(
                    "DB transaction failed. Programming error: %s. Rolling back.", error
                )
                session.rollback()
                raise error
            except DBAPIError as error:
                if error.connection_invalidated:
                    logger.warning("The connection got invalidated: %s", error)
                raise error
            session.commit()
            logger.debug(
                "Leaving database session manager. Took %s seconds",
                timer() - begin_time,
            )

    def dispose(self) -> None:
        """Dispose the engine"""
        if self.engine is not None:
            self.engine.dispose()
        logger.info("Disposed database connection pool")

    def get_users(self) -> List[User]:
        with self.connection() as session:
            return [
                User(**jsonable_encoder(user))
                for user in session.query(UserSchema).offset(0).limit(25).all()
            ]

    def add_user(self, user: User) -> None:
        with self.connection() as session:
            session.add(UserSchema(**user.dict()))

    def _get_user(self, session: Session, user_id: str) -> Optional[UserSchema]:
        return session.query(UserSchema).filter(UserSchema.user_id == user_id).first()

    def get_user(self, user_id: str) -> Optional[User]:
        with self.connection() as session:
            return User(**jsonable_encoder(self._get_user(session, user_id)))

    def delete_user(self, user_id: str) -> None:
        with self.connection() as session:
            session.delete(session.query(UserSchema).get(user_id))  # type: ignore

    def update_user(self, user_id: str, user_update: User) -> User:
        update = user_update.dict(exclude_unset=True)
        with self.connection() as session:
            user: UserSchema = session.query(UserSchema).get(user_id)  # type: ignore
            for key, value in update.items():
                setattr(user, key, value)
            session.add(user)
        return User(**jsonable_encoder(user))

    def get_groups(self) -> List[NamedGroup | Group]:
        with self.connection() as session:
            groups: List[GroupSchema] = (
                session.query(GroupSchema).offset(0).limit(25).all()
            )
            return [
                NamedGroup(**jsonable_encoder(group))
                if group.name is not None
                else Group(**jsonable_encoder(group))
                for group in groups
            ]

    def add_group(self, group: NamedGroup) -> None:
        with self.connection() as session:
            group_as_schema = self._to_db_schema(group)
            for user in group.users:
                user_from_db = self._get_user(session, user.user_id)
                assert (
                    user_from_db is not None
                ), "Can't create group as one of the users to add does not exist"
                group_as_schema.users.append(user_from_db)
            session.add(group_as_schema)

    def _get_group(self, session: Session, group_id: str) -> Optional[GroupSchema]:
        group: GroupSchema = session.query(GroupSchema).get(group_id)  # type: ignore
        return group

    def get_group(self, group_id: str) -> Optional[Group]:
        with self.connection() as session:
            return Group(**jsonable_encoder(self._get_group(session, group_id)))

    def update_group(self, group_id: str, group_update: NamedGroup) -> NamedGroup:
        update = group_update.dict(exclude_unset=True)
        with self.connection() as session:
            group: GroupSchema = session.query(GroupSchema).get(group_id)  # type: ignore
            for key, value in update.items():
                setattr(group, key, value)
            session.add(group)
        return NamedGroup(**jsonable_encoder(group))

    def delete_group(self, group_id: str) -> None:
        with self.connection() as session:
            session.delete(session.query(UserSchema).get(group_id))  # type: ignore

    def users(self) -> Dict[str, User]:
        return {user.user_id: user for user in self.get_users()}

    def groups(self) -> Dict[str, NamedGroup | Group | None]:
        return {group.group_id: group for group in self.get_groups()}

    def _to_db_schema(self, group: NamedGroup) -> GroupSchema:
        """
        Convert a Group into a GroupSchema without recursion issues

        Retrieves users from the database as User schema and turn transactions
        into Transaction schema objects which are then inserted into the database
        as well as a cascade.
        """
        group_dict = group.dict(exclude={"users", "transactions"})
        transactions_schemas = [
            TransactionSchema(**transaction.dict(exclude={"groups"}))
            for transaction in group.transactions
        ]
        group_dict["users"] = []
        group_dict["transactions"] = transactions_schemas
        return GroupSchema(**group_dict)

    def init_database_tables(self) -> None:
        """Initialize database tables"""
        Base.metadata.create_all(self.engine)

    def dispose_database_tables(self) -> None:
        """
        Dispose all database tables (destructive)

        Intended for test environments
        """
        Base.metadata.drop_all(self.engine)

    class Config:
        arbitrary_types_allowed = True
