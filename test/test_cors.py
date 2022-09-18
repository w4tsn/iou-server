import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from iou.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_response_cors_headers_origins(iou_client: AsyncClient) -> None:
    """Test correct CORS headers set in response"""
    response = await iou_client.get("/", headers={"origin": "http://localhost:8000"})
    assert response.status_code == 200
    assert "access-control-allow-credentials" in response.headers
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://localhost:8000"


@pytest.mark.asyncio
async def test_response_cors_headers_origins_regex(iou_client: AsyncClient) -> None:
    """Test CORS header regex"""
    response = await iou_client.get(
        "/", headers={"origin": "https://iou.notourserver.de"}
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert (
        response.headers["access-control-allow-origin"] == "https://iou.notourserver.de"
    )
