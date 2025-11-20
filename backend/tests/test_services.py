import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_service_crud_flow(test_client: AsyncClient):
    payload = {"email": "svc@example.com", "username": "svcuser", "password": "StrongPass123!"}
    resp = await test_client.post("/api/auth/register", json=payload)
    assert resp.status_code == 201
    login_resp = await test_client.post("/api/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert login_resp.status_code == 200

    create_resp = await test_client.post(
        "/api/services/",
        json={
            "name": "Danışmanlık",
            "description": "Strateji seansı",
            "price_amount": 1500.0,
            "price_currency": "TRY",
            "duration_minutes": 60,
        },
    )
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["name"] == "Danışmanlık"

    list_resp = await test_client.get("/api/services/")
    assert list_resp.status_code == 200
    services = list_resp.json()
    assert len(services) == 1

    service_id = services[0]["id"]
    update_resp = await test_client.put(
        f"/api/services/{service_id}",
        json={"price_amount": 2000.0, "duration_minutes": 90, "status": "inactive"},
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["price_amount"] == 2000.0
    assert updated["status"] == "inactive"

    delete_resp = await test_client.delete(f"/api/services/{service_id}")
    assert delete_resp.status_code == 204

    list_after = await test_client.get("/api/services/")
    assert list_after.status_code == 200
    assert list_after.json() == []
