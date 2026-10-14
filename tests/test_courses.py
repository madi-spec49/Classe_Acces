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


def course_payload(teacher_id, start="10:00:00", end="11:30:00"):
    return {
        "teacher_id": teacher_id,
        "title": "Mathématiques niveau 1",
        "subject": "Mathématiques",
        "day_of_week": 6,
        "start_time": start,
        "end_time": end,
        "zoom_link": "https://zoom.us/j/123456789",
    }


@pytest.fixture
def staff_token(client):
    data = register(client, "staff@example.com")
    set_role("staff@example.com", "staff")
    return data["access_token"]


@pytest.fixture
def student_token(client):
    return register(client, "eleve@example.com")["access_token"]


@pytest.fixture
def teacher_id(client):
    data = register(client, "prof@example.com")
    set_role("prof@example.com", "teacher")
    return data["user"]["id"]


def test_staff_can_create_course(client, staff_token, teacher_id):
    response = client.post(
        "/api/courses",
        json=course_payload(teacher_id),
        headers={"Authorization": f"Bearer {staff_token}"},
    )

    assert response.status_code == 200
    assert response.json()["teacher_id"] == teacher_id


def test_student_cannot_create_course(client, student_token, teacher_id):
    response = client.post(
        "/api/courses",
        json=course_payload(teacher_id),
        headers={"Authorization": f"Bearer {student_token}"},
    )

    assert response.status_code == 403


def test_course_teacher_must_be_a_teacher(client, staff_token):
    student_id = register(client, "autre-eleve@example.com")["user"]["id"]

    response = client.post(
        "/api/courses",
        json=course_payload(student_id),
        headers={"Authorization": f"Bearer {staff_token}"},
    )

    assert response.status_code == 400


def test_end_time_before_start_time_returns_422(client, staff_token, teacher_id):
    response = client.post(
        "/api/courses",
        json=course_payload(teacher_id, start="11:00:00", end="10:00:00"),
        headers={"Authorization": f"Bearer {staff_token}"},
    )

    assert response.status_code == 422


def test_student_can_list_courses(client, staff_token, student_token, teacher_id):
    client.post(
        "/api/courses",
        json=course_payload(teacher_id),
        headers={"Authorization": f"Bearer {staff_token}"},
    )

    response = client.get(
        "/api/courses",
        headers={"Authorization": f"Bearer {student_token}"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def create_course_for_test(client, staff_token, teacher_id):
    response = client.post(
        "/api/courses",
        json=course_payload(teacher_id),
        headers={"Authorization": f"Bearer {staff_token}"},
    )
    return response.json()["id"]


def session_payload():
    return {"date": "2026-10-18T10:00:00", "zoom_link": "https://zoom.us/j/123456789"}


def test_staff_can_create_session(client, staff_token, teacher_id):
    course_id = create_course_for_test(client, staff_token, teacher_id)

    response = client.post(
        f"/api/courses/{course_id}/sessions",
        json=session_payload(),
        headers={"Authorization": f"Bearer {staff_token}"},
    )

    assert response.status_code == 200
    assert response.json()["course_id"] == course_id


def test_student_cannot_create_session(client, staff_token, student_token, teacher_id):
    course_id = create_course_for_test(client, staff_token, teacher_id)

    response = client.post(
        f"/api/courses/{course_id}/sessions",
        json=session_payload(),
        headers={"Authorization": f"Bearer {student_token}"},
    )

    assert response.status_code == 403


def test_session_on_unknown_course_returns_404(client, staff_token):
    response = client.post(
        "/api/courses/999/sessions",
        json=session_payload(),
        headers={"Authorization": f"Bearer {staff_token}"},
    )

    assert response.status_code == 404


def test_student_can_list_sessions(client, staff_token, student_token, teacher_id):
    course_id = create_course_for_test(client, staff_token, teacher_id)
    client.post(
        f"/api/courses/{course_id}/sessions",
        json=session_payload(),
        headers={"Authorization": f"Bearer {staff_token}"},
    )

    response = client.get(
        f"/api/courses/{course_id}/sessions",
        headers={"Authorization": f"Bearer {student_token}"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
