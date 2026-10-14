import pytest

from app.config import get_db
from app.main import app
from app.models import User


def set_role(email, role):
    # Récupère une session branchée sur la base de test (celle de conftest.py)
    db_gen = app.dependency_overrides[get_db]()
    db = next(db_gen)
    try:
        db.query(User).filter(User.email == email).update({"role": role})
        db.commit()
    finally:
        db_gen.close()


def register(client, email):
    response = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "monMotDePasse123",
            "first_name": "Test",
            "last_name": "User",
        },
    )
    return response.json()


def auth(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def staff_token(client):
    data = register(client, "staff-reg@example.com")
    set_role("staff-reg@example.com", "staff")
    return data["access_token"]


@pytest.fixture
def student(client):
    return register(client, "eleve-reg@example.com")


@pytest.fixture
def course_id(client, staff_token):
    teacher = register(client, "prof-reg@example.com")
    set_role("prof-reg@example.com", "teacher")
    response = client.post(
        "/api/courses",
        json={
            "teacher_id": teacher["user"]["id"],
            "title": "Physique",
            "subject": "Sciences",
            "day_of_week": 6,
            "start_time": "10:00:00",
            "end_time": "11:30:00",
        },
        headers=auth(staff_token),
    )
    return response.json()["id"]


def test_student_can_request_enrollment(client, student, course_id):
    response = client.post(
        "/api/registrations",
        json={"course_id": course_id},
        headers=auth(student["access_token"]),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "pending"


def test_duplicate_request_returns_400(client, student, course_id):
    headers = auth(student["access_token"])
    client.post("/api/registrations", json={"course_id": course_id}, headers=headers)

    response = client.post("/api/registrations", json={"course_id": course_id}, headers=headers)

    assert response.status_code == 400


def test_request_unknown_course_returns_404(client, student):
    response = client.post(
        "/api/registrations",
        json={"course_id": 999},
        headers=auth(student["access_token"]),
    )

    assert response.status_code == 404


def test_staff_can_approve_request(client, student, staff_token, course_id):
    created = client.post(
        "/api/registrations",
        json={"course_id": course_id},
        headers=auth(student["access_token"]),
    )
    enrollment_id = created.json()["id"]

    response = client.patch(
        f"/api/registrations/{enrollment_id}",
        json={"status": "approved"},
        headers=auth(staff_token),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "approved"


def test_student_cannot_approve_request(client, student, course_id):
    created = client.post(
        "/api/registrations",
        json={"course_id": course_id},
        headers=auth(student["access_token"]),
    )
    enrollment_id = created.json()["id"]

    response = client.patch(
        f"/api/registrations/{enrollment_id}",
        json={"status": "approved"},
        headers=auth(student["access_token"]),
    )

    assert response.status_code == 403
