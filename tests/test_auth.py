USER = {
    "email": "test_pytest@example.com",
    "password": "monMotDePasse123",
    "first_name": "Test",
    "last_name": "Pytest",
    "role": "student",
}


def test_register_returns_token(client):
    response = client.post("/api/auth/register", json=USER)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_register_duplicate_email_returns_400(client):
    client.post("/api/auth/register", json=USER)
    response = client.post("/api/auth/register", json=USER)
    assert response.status_code == 400


def test_login_success(client):
    client.post("/api/auth/register", json=USER)
    response = client.post(
        "/api/auth/login",
        json={"email": USER["email"], "password": USER["password"]},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password_returns_401(client):
    client.post("/api/auth/register", json=USER)
    response = client.post(
        "/api/auth/login",
        json={"email": USER["email"], "password": "mauvais"},
    )
    assert response.status_code == 401


def test_me_with_valid_token(client):
    token = client.post("/api/auth/register", json=USER).json()["access_token"]
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == USER["email"]


def test_me_without_token_returns_403(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 403


def test_me_with_invalid_token_returns_401(client):
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer abc.def.ghi"})
    assert response.status_code == 401