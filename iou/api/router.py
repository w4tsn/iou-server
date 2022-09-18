from fastapi import APIRouter

from iou.api.v1 import groups, users

api_router = APIRouter(prefix="/v1")

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(groups.router, prefix="/groups", tags=["groups"])
