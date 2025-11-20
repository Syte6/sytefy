import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_list_appointments(test_client: AsyncClient):
    user_payload = {"email": "apt@example.com", "username": "aptuser", "password": "StrongPass123!"}
    resp = await test_client.post("/api/auth/register", json=user_payload)
    assert resp.status_code == 201
    login = await test_client.post("/api/auth/login", json={"email": user_payload["email"], "password": user_payload["password"]})
    assert login.status_code == 200

    start = datetime.now(timezone.utc) + timedelta(hours=2)
    end = start + timedelta(hours=1)
    appointment_payload = {
        "title": "Danışmanlık",
        "description": "Finansal plan",
        "location": "Ofis",
        "channel": "in_person",
        "start_at": start.isoformat(),
        "end_at": end.isoformat(),
        "reminder_channels": ["log"],
    }
    create_resp = await test_client.post("/api/appointments/", json=appointment_payload)
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["title"] == appointment_payload["title"]
    assert created["status"] == "scheduled"

    list_resp = await test_client.get("/api/appointments/?limit=5&offset=0")
    assert list_resp.status_code == 200
    data = list_resp.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1
    appointment_id = data["items"][0]["id"]
    assert data["items"][0]["reminder_channels"] == ["log"]

    update_resp = await test_client.put(
        f"/api/appointments/{appointment_id}",
        json={
            "title": "Güncellenmiş",
            "reminder_channels": ["log", "email"],
        },
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "Güncellenmiş"
    assert update_resp.json()["reminder_channels"] == ["log", "email"]

    cancel_resp = await test_client.post(f"/api/appointments/{appointment_id}/cancel")
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "cancelled"


@pytest.mark.asyncio
async def test_status_transition_rules(test_client: AsyncClient):
    user_payload = {"email": "apt2@example.com", "username": "aptuser2", "password": "StrongPass123!"}
    resp = await test_client.post("/api/auth/register", json=user_payload)
    assert resp.status_code == 201
    login = await test_client.post("/api/auth/login", json={"email": user_payload["email"], "password": user_payload["password"]})
    assert login.status_code == 200

    start = datetime.now(timezone.utc) + timedelta(hours=3)
    end = start + timedelta(hours=1)
    create_resp = await test_client.post(
        "/api/appointments/",
        json={
            "title": "Kontrol",
            "start_at": start.isoformat(),
            "end_at": end.isoformat(),
        },
    )
    assert create_resp.status_code == 201
    appointment_id = create_resp.json()["id"]

    invalid_status = await test_client.put(f"/api/appointments/{appointment_id}", json={"status": "invalid"})
    assert invalid_status.status_code == 400

    complete_resp = await test_client.put(f"/api/appointments/{appointment_id}", json={"status": "completed"})
    assert complete_resp.status_code == 200
    assert complete_resp.json()["status"] == "completed"

    revert_resp = await test_client.put(f"/api/appointments/{appointment_id}", json={"status": "scheduled"})
    assert revert_resp.status_code == 400

    cancel_after_complete = await test_client.post(f"/api/appointments/{appointment_id}/cancel")
    assert cancel_after_complete.status_code == 400


@pytest.mark.asyncio
async def test_download_appointment_ics(test_client: AsyncClient):
    payload = {"email": "ics@example.com", "username": "icsuser", "password": "StrongPass123!"}
    resp = await test_client.post("/api/auth/register", json=payload)
    assert resp.status_code == 201
    login = await test_client.post("/api/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert login.status_code == 200

    start = datetime.now(timezone.utc) + timedelta(hours=1)
    end = start + timedelta(hours=1)
    appointment_resp = await test_client.post(
        "/api/appointments/",
        json={
            "title": "Takip Görüşmesi",
            "description": "ICS testi",
            "location": "Online",
            "start_at": start.isoformat(),
            "end_at": end.isoformat(),
        },
    )
    assert appointment_resp.status_code == 201
    appointment_id = appointment_resp.json()["id"]

    ics_resp = await test_client.get(f"/api/appointments/{appointment_id}/ics")
    assert ics_resp.status_code == 200
    assert ics_resp.headers["content-type"].startswith("text/calendar")
    body = ics_resp.text
    assert "BEGIN:VEVENT" in body
    assert "SUMMARY:Takip Görüşmesi" in body
