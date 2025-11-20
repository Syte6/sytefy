import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_metrics_endpoint_reports_requests(test_client: AsyncClient):
    health = await test_client.get("/api/health")
    assert health.status_code == 200

    metrics_resp = await test_client.get("/metrics")
    assert metrics_resp.status_code == 200
    body = metrics_resp.text
    assert "sytefy_requests_total" in body
    assert 'path="/api/health"' in body
