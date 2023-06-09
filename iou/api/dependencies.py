from fastapi import HTTPException, Request, status

from iou.db.db_interface import IouDBInterface
from iou.db.sql_db import SqlDb
from iou.security import (
    Authentication,
    AuthenticationError,
    AuthenticationPreAuthenticated,
)


def get_db() -> IouDBInterface:
    return SqlDb.instance()


def get_authentication(request: Request) -> Authentication:
    """Retrieve the Authentication from the incoming request"""
    try:
        return AuthenticationPreAuthenticated.from_headers(
            dict(request.headers.items())
        )
    except AuthenticationError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)
        ) from error
