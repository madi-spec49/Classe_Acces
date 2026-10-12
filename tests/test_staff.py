def register_student(client, email):
    response = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "monMotDePasse123",
            "first_name": "Lina",
            "last_name": "Durand",
        },
    )
    return response.json()["access_token"]


def teacher_payload(email):
    return {
        "email": email,
        "password": "monMotDePasse123",
        "first_name": "Paul",
        "last_name": "Martin",
    }


def test_student_cannot_create_teacher(client):
    token = register_student(client, "eleve@example.com")

    response = client.post(
        "/api/staff/teachers",
        json=teacher_payload("prof@example.com"),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_create_teacher_without_token_returns_403(client):
    response = client.post(
        "/api/staff/teachers",
        json=teacher_payload("prof@example.com"),
    )

    assert response.status_code == 403