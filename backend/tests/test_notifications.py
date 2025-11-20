import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_notification_flow(test_client: AsyncClient):
    payload = {"email": "notif@example.com", "username": "notifuser", "password": "StrongPass123!"}
    resp = await test_client.post("/api/auth/register", json=payload)
    assert resp.status_code == 201
    login = await test_client.post("/api/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert login.status_code == 200

    create = await test_client.post(
        "/api/notifications/",
        json={
            "user_id": 1,
            "title": "Sistem",
            "body": "Yeni randevu oluşturuldu",
            "channel": "log",
        },
    )
    assert create.status_code == 201
    notification_id = create.json()["id"]

    list_resp = await test_client.get("/api/notifications/")
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 1

    mark_resp = await test_client.post(f"/api/notifications/{notification_id}/read")
    assert mark_resp.status_code == 200
    assert mark_resp.json()["status"] == "read"
