from helpers import PASSWORD, auth


def test_login_success_returns_token(client, make_user):
    make_user("login.ok@example.com")

    response = client.post(
        "/api/auth/login",
        json={"email": "login.ok@example.com", "password": PASSWORD},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password_returns_401(client, make_user):
    make_user("login.ko@example.com")

    response = client.post(
        "/api/auth/login",
        json={"email": "login.ko@example.com", "password": "mauvais"},
    )

    assert response.status_code == 401


def test_me_with_valid_token(client, make_user):
    token, _ = make_user("me@example.com")

    response = client.get("/api/auth/me", headers=auth(token))

    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


def test_me_without_token_returns_403(client):
    response = client.get("/api/auth/me")

    assert response.status_code == 403


def test_me_with_invalid_token_returns_401(client):
    response = client.get("/api/auth/me", headers=auth("abc.def.ghi"))

    assert response.status_code == 401
