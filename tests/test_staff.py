from helpers import auth


def teacher_payload(email):
    return {
        "email": email,
        "password": "monMotDePasse123",
        "first_name": "Paul",
        "last_name": "Martin",
    }


def test_student_cannot_create_teacher(client, make_user):
    token, _ = make_user("eleve.staff@example.com", role="student")

    response = client.post(
        "/api/staff/teachers",
        json=teacher_payload("prof@example.com"),
        headers=auth(token),
    )

    assert response.status_code == 403


def test_staff_can_create_teacher(client, make_user):
    token, _ = make_user("staff.create@example.com", role="staff")

    response = client.post(
        "/api/staff/teachers",
        json=teacher_payload("prof.nouveau@example.com"),
        headers=auth(token),
    )

    assert response.status_code == 200
    assert response.json()["role"] == "teacher"


def test_create_teacher_without_token_returns_403(client):
    response = client.post(
        "/api/staff/teachers",
        json=teacher_payload("prof@example.com"),
    )

    assert response.status_code == 403
