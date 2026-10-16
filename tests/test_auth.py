from datetime import timedelta

from src.core.security import ACCESS, REFRESH, create_token
from tests.conftest import auth_header, login, register


# ---------------- registration ----------------
async def test_register_success(client):
    r = await register(client)
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == "a@example.com"
    assert body["role"] == "user"
    assert "password" not in body and "hashed_password" not in body


async def test_register_duplicate_email_and_username(client):
    await register(client)
    r = await register(client, username="other")
    assert r.status_code == 409
    r = await register(client, email="b@example.com")
    assert r.status_code == 409


async def test_register_cannot_self_assign_admin(client):
    r = await client.post(
        "/api/auth/register",
        json={"email": "x@example.com", "username": "x_user", "password": "secret123", "role": "admin"},
    )
    assert r.status_code == 201
    assert r.json()["role"] == "user"


async def test_register_weak_password(client):
    assert (await register(client, password="short1")).status_code == 422
    assert (await register(client, password="allletters")).status_code == 422
    assert (await register(client, password="12345678")).status_code == 422


# ---------------- login / tokens ----------------
async def test_login_with_username_and_email(client):
    await register(client)
    assert (await login(client, "alice")).status_code == 200
    assert (await login(client, "a@example.com")).status_code == 200


async def test_login_wrong_password(client):
    await register(client)
    assert (await login(client, "alice", "wrongpass1")).status_code == 401


async def test_me_requires_token(client):
    assert (await client.get("/api/users/me")).status_code == 401
    assert (await client.get("/api/users/me", headers=auth_header("garbage"))).status_code == 401


async def test_me_with_token(client, user_token):
    r = await client.get("/api/users/me", headers=auth_header(user_token))
    assert r.status_code == 200
    assert r.json()["username"] == "alice"


async def test_refresh_flow(client):
    await register(client)
    tokens = (await login(client)).json()
    r = await client.post("/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r.status_code == 200
    assert (await client.get("/api/users/me", headers=auth_header(r.json()["access_token"]))).status_code == 200


async def test_token_type_confusion_rejected(client):
    await register(client)
    tokens = (await login(client)).json()
    # refresh token must not work as access token
    r = await client.get("/api/users/me", headers=auth_header(tokens["refresh_token"]))
    assert r.status_code == 401
    # access token must not work as refresh token
    r = await client.post("/api/auth/refresh", json={"refresh_token": tokens["access_token"]})
    assert r.status_code == 401


async def test_expired_token_rejected(client):
    await register(client)
    expired = create_token(1, ACCESS, timedelta(seconds=-5))
    assert (await client.get("/api/users/me", headers=auth_header(expired))).status_code == 401
    expired_refresh = create_token(1, REFRESH, timedelta(seconds=-5))
    r = await client.post("/api/auth/refresh", json={"refresh_token": expired_refresh})
    assert r.status_code == 401


# ---------------- profile ----------------
async def test_update_profile(client, user_token):
    r = await client.patch(
        "/api/users/me", json={"full_name": "Alice A"}, headers=auth_header(user_token)
    )
    assert r.status_code == 200
    assert r.json()["full_name"] == "Alice A"


async def test_update_profile_conflict(client, user_token):
    await register(client, email="b@example.com", username="bob")
    r = await client.patch("/api/users/me", json={"username": "bob"}, headers=auth_header(user_token))
    assert r.status_code == 409


async def test_user_cannot_change_own_role(client, user_token):
    r = await client.patch("/api/users/me", json={"role": "admin"}, headers=auth_header(user_token))
    assert r.status_code == 200
    assert r.json()["role"] == "user"


async def test_change_password(client, user_token):
    h = auth_header(user_token)
    bad = await client.post(
        "/api/users/me/change-password",
        json={"current_password": "nope12345", "new_password": "newsecret1"},
        headers=h,
    )
    assert bad.status_code == 400
    ok = await client.post(
        "/api/users/me/change-password",
        json={"current_password": "secret123", "new_password": "newsecret1"},
        headers=h,
    )
    assert ok.status_code == 204
    assert (await login(client, "alice", "secret123")).status_code == 401
    assert (await login(client, "alice", "newsecret1")).status_code == 200


# ---------------- authorization (RBAC) ----------------
async def test_normal_user_forbidden_on_admin_routes(client, user_token):
    h = auth_header(user_token)
    assert (await client.get("/api/users", headers=h)).status_code == 403
    assert (await client.get("/api/users/1", headers=h)).status_code == 403
    assert (await client.patch("/api/users/1", json={"is_active": False}, headers=h)).status_code == 403
    assert (await client.delete("/api/users/1", headers=h)).status_code == 403


async def test_admin_can_list_and_get(client, user_token, admin_token):
    h = auth_header(admin_token)
    r = await client.get("/api/users", headers=h)
    assert r.status_code == 200
    assert len(r.json()) == 2
    uid = next(u["id"] for u in r.json() if u["username"] == "alice")
    assert (await client.get(f"/api/users/{uid}", headers=h)).json()["username"] == "alice"
    assert (await client.get("/api/users/9999", headers=h)).status_code == 404


async def test_admin_can_change_role_and_deactivate(client, user_token, admin_token):
    h = auth_header(admin_token)
    uid = (await client.get("/api/users/me", headers=auth_header(user_token))).json()["id"]

    r = await client.patch(f"/api/users/{uid}", json={"role": "admin"}, headers=h)
    assert r.json()["role"] == "admin"

    r = await client.patch(f"/api/users/{uid}", json={"is_active": False}, headers=h)
    assert r.json()["is_active"] is False

    # deactivated user: existing token and new login both blocked
    assert (await client.get("/api/users/me", headers=auth_header(user_token))).status_code == 403
    assert (await login(client)).status_code == 403


async def test_admin_cannot_demote_or_delete_self(client, admin_token):
    h = auth_header(admin_token)
    me = (await client.get("/api/users/me", headers=h)).json()["id"]
    assert (await client.patch(f"/api/users/{me}", json={"role": "user"}, headers=h)).status_code == 400
    assert (await client.delete(f"/api/users/{me}", headers=h)).status_code == 400


async def test_admin_delete_user(client, user_token, admin_token):
    h = auth_header(admin_token)
    uid = (await client.get("/api/users/me", headers=auth_header(user_token))).json()["id"]
    assert (await client.delete(f"/api/users/{uid}", headers=h)).status_code == 204
    assert (await client.get(f"/api/users/{uid}", headers=h)).status_code == 404
