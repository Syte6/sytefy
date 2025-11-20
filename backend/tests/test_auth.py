import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login_flow(test_client: AsyncClient):
    register_payload = {
        "email": "test@example.com",
        "username": "tester",
        "password": "VerySecure123!",
    }
    resp = await test_client.post("/api/auth/register", json=register_payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == register_payload["email"]

    login_payload = {"email": register_payload["email"], "password": register_payload["password"]}
    login_resp = await test_client.post("/api/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    tokens = login_resp.json()
    assert "access_token" in tokens and "refresh_token" in tokens
    assert test_client.cookies.get("sytefy_access_token") is not None
    assert test_client.cookies.get("sytefy_refresh_token") is not None

    me_resp = await test_client.get("/api/auth/me")
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == register_payload["email"]


@pytest.mark.asyncio
async def test_refresh_rotates_token(test_client: AsyncClient):
    await test_client.post(
        "/api/auth/register",
        json={
            "email": "rotate@example.com",
            "username": "rotate",
            "password": "RotatePassword123!",
        },
    )
    await test_client.post(
        "/api/auth/login",
        json={"email": "rotate@example.com", "password": "RotatePassword123!"},
    )

    refresh_resp = await test_client.post("/api/auth/refresh")
    assert refresh_resp.status_code == 200
    refreshed = refresh_resp.json()
    assert "access_token" in refreshed
    assert "refresh_token" in refreshed

    customers_resp = await test_client.get("/api/customers/")
    assert customers_resp.status_code == 200
