import pytest
import asyncio
from httpx import AsyncClient

from iou.main import app


@pytest.fixture(scope="session")
def event_loop():
    """
    This very important fixture loads one asyncio event loop for the whole pytest session.
    Missing out on this point leads to much headache as there might be multiple event
    loops.
    """
    return asyncio.get_event_loop()


@pytest.fixture
async def iou_client() -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
