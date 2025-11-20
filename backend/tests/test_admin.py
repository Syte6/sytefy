import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_role_and_mfa_management(test_client: AsyncClient):
    owner = {"email": "owner@example.com", "username": "owner", "password": "OwnerPass123!"}
    staff = {"email": "staff@example.com", "username": "staff", "password": "StaffPass123!"}

    resp_owner = await test_client.post("/api/auth/register", json=owner)
    assert resp_owner.status_code == 201
    login_owner = await test_client.post("/api/auth/login", json={"email": owner["email"], "password": owner["password"]})
    assert login_owner.status_code == 200

    resp_staff = await test_client.post("/api/auth/register", json=staff)
    assert resp_staff.status_code == 201

    roles_resp = await test_client.get("/api/users/admin/roles")
    assert roles_resp.status_code == 200
    roles = roles_resp.json()
    assert any(role["slug"] == "staff" for role in roles)

    accounts_resp = await test_client.get("/api/users/admin/accounts")
    assert accounts_resp.status_code == 200
    accounts = accounts_resp.json()
    assert len(accounts) == 2
    target = next(acc for acc in accounts if acc["email"] == staff["email"])

    update_role = await test_client.patch(
        f"/api/users/admin/accounts/{target['id']}/role",
        json={"role": "staff"},
    )
    assert update_role.status_code == 200
    assert update_role.json()["role"] == "staff"

    update_mfa = await test_client.patch(
        f"/api/users/admin/accounts/{target['id']}/mfa",
        json={"enabled": True},
    )
    assert update_mfa.status_code == 200
    assert update_mfa.json()["mfa_enabled"] is True

    refreshed_accounts = await test_client.get("/api/users/admin/accounts")
    assert refreshed_accounts.status_code == 200
    updated_target = next(acc for acc in refreshed_accounts.json() if acc["email"] == staff["email"])
    assert updated_target["role"] == "staff"
    assert updated_target["mfa_enabled"] is True
