from app.models.enums import UserRole


def test_login_success_returns_tokens(client, user_factory):
    user_factory(UserRole.admin)
    resp = client.post(
        "/auth/login",
        json={"email": "admin@who.int", "password": "Password123!"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["token_type"] == "bearer"


def test_login_wrong_password_returns_401(client, user_factory):
    user_factory(UserRole.admin)
    resp = client.post(
        "/auth/login",
        json={"email": "admin@who.int", "password": "wrong"},
    )
    assert resp.status_code == 401


def test_me_without_token_returns_401(client):
    assert client.get("/auth/me").status_code == 401  # no credentials -> HTTPBearer


def test_me_with_invalid_token_returns_401_not_500(client):
    resp = client.get(
        "/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert resp.status_code == 401


def test_me_with_valid_token(client, auth_headers):
    resp = client.get("/auth/me", headers=auth_headers(UserRole.field_worker))
    assert resp.status_code == 200
    assert resp.json()["role"] == "field_worker"


def test_refresh_flow(client, user_factory):
    user_factory(UserRole.admin)
    tokens = client.post(
        "/auth/login",
        json={"email": "admin@who.int", "password": "Password123!"},
    ).json()
    resp = client.post(
        "/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert resp.status_code == 200
    assert resp.json()["access_token"]


def test_refresh_rejects_access_token(client, user_factory):
    user_factory(UserRole.admin)
    tokens = client.post(
        "/auth/login",
        json={"email": "admin@who.int", "password": "Password123!"},
    ).json()
    # An access token must not be accepted at the refresh endpoint.
    resp = client.post(
        "/auth/refresh", json={"refresh_token": tokens["access_token"]}
    )
    assert resp.status_code == 401
