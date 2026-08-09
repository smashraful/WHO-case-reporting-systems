from app.models.enums import UserRole


def test_create_user_requires_admin(client, auth_headers):
    payload = {
        "full_name": "New Worker",
        "email": "new@who.int",
        "password": "Password123!",
        "role": "field_worker",
    }
    # field_worker cannot create users
    resp = client.post(
        "/users", json=payload, headers=auth_headers(UserRole.field_worker)
    )
    assert resp.status_code == 403

    # admin can
    resp = client.post("/users", json=payload, headers=auth_headers(UserRole.admin))
    assert resp.status_code == 201
    assert resp.json()["email"] == "new@who.int"


def test_create_duplicate_email_returns_409(client, auth_headers):
    payload = {
        "full_name": "Dup",
        "email": "dup@who.int",
        "password": "Password123!",
    }
    headers = auth_headers(UserRole.admin)
    assert client.post("/users", json=payload, headers=headers).status_code == 201
    resp = client.post("/users", json=payload, headers=headers)
    assert resp.status_code == 409


def test_get_user_by_id_requires_privileged_role(client, auth_headers, user_factory):
    target = user_factory(UserRole.lab_staff)
    # field_worker is not allowed to read arbitrary users
    resp = client.get(
        f"/users/{target.id}", headers=auth_headers(UserRole.field_worker)
    )
    assert resp.status_code == 403


def test_delete_user_requires_admin(client, auth_headers, user_factory):
    target = user_factory(UserRole.lab_staff)
    resp = client.delete(
        f"/users/{target.id}", headers=auth_headers(UserRole.district_officer)
    )
    assert resp.status_code == 403

    resp = client.delete(
        f"/users/{target.id}", headers=auth_headers(UserRole.admin)
    )
    assert resp.status_code == 200


def test_delete_user_without_token_is_blocked(client, user_factory):
    target = user_factory(UserRole.lab_staff)
    # The previously-open delete endpoint must now reject anonymous callers.
    assert client.delete(f"/users/{target.id}").status_code == 401
