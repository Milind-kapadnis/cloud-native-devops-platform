import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def new_user():
    tag = uuid.uuid4().hex[:8]
    return {
        "username": f"user_{tag}",
        "email": f"{tag}@example.com",
        "password": "TestPassword123!",
    }


def register(user):
    return client.post("/register", json=user)


def login_token(user):
    response = client.post(
        "/login",
        json={"username": user["username"], "password": user["password"]},
    )
    return response.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_register_success():
    user = new_user()
    response = register(user)
    assert response.status_code == 200
    assert response.json()["username"] == user["username"]
    assert "password" not in response.json()


def test_register_duplicate_username():
    user = new_user()
    register(user)
    other = new_user()
    other["username"] = user["username"]
    assert register(other).status_code == 400


def test_register_duplicate_email():
    user = new_user()
    register(user)
    other = new_user()
    other["email"] = user["email"]
    assert register(other).status_code == 400


def test_login_success():
    user = new_user()
    register(user)
    response = client.post(
        "/login",
        json={"username": user["username"], "password": user["password"]},
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password_returns_401():
    user = new_user()
    register(user)
    response = client.post(
        "/login",
        json={"username": user["username"], "password": "wrong"},
    )
    assert response.status_code == 401


def test_me_with_valid_token():
    user = new_user()
    register(user)
    response = client.get("/me", headers=auth(login_token(user)))
    assert response.status_code == 200
    assert response.json() == {"username": user["username"]}


def test_me_without_token():
    assert client.get("/me").status_code == 401


def test_me_with_invalid_token():
    assert client.get("/me", headers=auth("bad-token")).status_code == 401


def test_get_missing_user_returns_404():
    user = new_user()
    register(user)
    response = client.get("/users/99999999", headers=auth(login_token(user)))
    assert response.status_code == 404


def test_update_own_account():
    user = new_user()
    user_id = register(user).json()["id"]
    new_email = "new_" + user["email"]
    response = client.put(
        f"/users/{user_id}",
        json={"username": user["username"], "email": new_email},
        headers=auth(login_token(user)),
    )
    assert response.status_code == 200
    assert response.json()["email"] == new_email


def test_update_to_existing_username_returns_400():
    first = new_user()
    second = new_user()
    register(first)
    second_id = register(second).json()["id"]
    response = client.put(
        f"/users/{second_id}",
        json={"username": first["username"], "email": second["email"]},
        headers=auth(login_token(second)),
    )
    assert response.status_code == 400


def test_cannot_update_another_user():
    owner = new_user()
    attacker = new_user()
    owner_id = register(owner).json()["id"]
    register(attacker)
    response = client.put(
        f"/users/{owner_id}",
        json={"username": owner["username"], "email": "x@example.com"},
        headers=auth(login_token(attacker)),
    )
    assert response.status_code == 403


def test_cannot_delete_another_user():
    owner = new_user()
    attacker = new_user()
    owner_id = register(owner).json()["id"]
    register(attacker)
    response = client.delete(
        f"/users/{owner_id}", headers=auth(login_token(attacker))
    )
    assert response.status_code == 403


def test_delete_own_account():
    user = new_user()
    user_id = register(user).json()["id"]
    headers = auth(login_token(user))
    assert client.delete(f"/users/{user_id}", headers=headers).status_code == 200
    assert client.get(f"/users/{user_id}", headers=headers).status_code == 404
