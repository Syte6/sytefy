import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_invoice_crud_flow(test_client: AsyncClient):
    user_payload = {"email": "invoice@example.com", "username": "invoiceuser", "password": "StrongPass123!"}
    resp = await test_client.post("/api/auth/register", json=user_payload)
    assert resp.status_code == 201
    login = await test_client.post("/api/auth/login", json={"email": user_payload["email"], "password": user_payload["password"]})
    assert login.status_code == 200

    due = datetime.now(timezone.utc) + timedelta(days=7)
    create_resp = await test_client.post(
        "/api/finances/invoices/",
        json={
            "title": "Danışmanlık Faturası",
            "amount": 1500.0,
            "currency": "TRY",
            "due_date": due.isoformat(),
            "description": "Aylık danışmanlık ücreti",
        },
    )
    assert create_resp.status_code == 201
    invoice_id = create_resp.json()["id"]
    assert create_resp.json()["status"] == "draft"

    list_resp = await test_client.get("/api/finances/invoices/")
    assert list_resp.status_code == 200
    rows = list_resp.json()
    assert len(rows) == 1
    assert rows[0]["number"].startswith("INV-")

    update_resp = await test_client.put(f"/api/finances/invoices/{invoice_id}", json={"status": "paid"})
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "paid"

    delete_resp = await test_client.delete(f"/api/finances/invoices/{invoice_id}")
    assert delete_resp.status_code == 204

    list_after = await test_client.get("/api/finances/invoices/")
    assert list_after.status_code == 200
    assert list_after.json() == []
