import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from iou._version import VERSION
from iou.api.router import api_router
from iou.config import load_log_config, settings

load_log_config(settings.IOU_LOG_CONFIG_FILE)

logger = logging.getLogger(__name__)

app = FastAPI(title="IOU")

if settings.IOU_CORS_ORIGINS or settings.IOU_CORS_ORIGIN_REGEX:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.IOU_CORS_ORIGINS,
        allow_origin_regex=settings.IOU_CORS_ORIGIN_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix="/api")


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "IOU as in I o(we) (yo)u"}


logger.info(
    "Started IOU main process in environment '%s' on http://%s:%s",
    settings.IOU_ENVIRONMENT.value,
    settings.IOU_SERVER_HOST,
    settings.IOU_SERVER_PORT,
)
logger.info("Version: %s", VERSION)
