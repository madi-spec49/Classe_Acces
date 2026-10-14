import pytest

from app.config import get_db
from app.main import app
from app.models import User

PASSWORD = "monMotDePasse123"


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def login(client, email):
    response = client.post("/api/auth/login", json={"email": email, "password": PASSWORD})
    return response.json()["access_token"]


def set_role(email, role):
    db = next(app.dependency_overrides[get_db]())
    user = db.query(User).filter(User.email == email).first()
    user.role = role
    db.commit()
    db.close()


def make_user(client, email, role="student"):
    client.post(
        "/api/auth/register",
        json={"email": email, "password": PASSWORD, "first_name": "Test", "last_name": "User"},
    )
    if role != "student":
        set_role(email, role)
    token = login(client, email)
    user_id = client.get("/api/auth/me", headers=auth(token)).json()["id"]
    return token, user_id


@pytest.fixture
def data(client):
    staff_token, _ = make_user(client, "staff.prog@example.com", "staff")
    teacher_token, teacher_id = make_user(client, "prof.prog@example.com", "teacher")
    student_token, student_id = make_user(client, "eleve.prog@example.com")
    _, outsider_id = make_user(client, "outsider.prog@example.com")

    course = client.post(
        "/api/courses",
        headers=auth(staff_token),
        json={
            "teacher_id": teacher_id,
            "title": "Français",
            "subject": "Français",
            "day_of_week": 6,
            "start_time": "10:00",
            "end_time": "12:00",
            "zoom_link": "https://zoom.example.com/fr",
        },
    ).json()

    enrollment = client.post(
        "/api/registrations",
        headers=auth(student_token),
        json={"course_id": course["id"]},
    ).json()
    client.patch(
        f"/api/registrations/{enrollment['id']}",
        headers=auth(staff_token),
        json={"status": "approved"},
    )

    return {
        "staff_token": staff_token,
        "teacher_token": teacher_token,
        "student_token": student_token,
        "student_id": student_id,
        "outsider_id": outsider_id,
        "course_id": course["id"],
    }


def progress_payload(data, student_id=None):
    return {
        "student_id": student_id or data["student_id"],
        "course_id": data["course_id"],
        "level": "Niveau 2",
        "note": "Bon travail",
    }


def test_teacher_records_progress(client, data):
    response = client.post(
        "/api/progress",
        headers=auth(data["teacher_token"]),
        json=progress_payload(data),
    )
    assert response.status_code == 200
    assert response.json()["level"] == "Niveau 2"


def test_student_cannot_record_progress(client, data):
    response = client.post(
        "/api/progress",
        headers=auth(data["student_token"]),
        json=progress_payload(data),
    )
    assert response.status_code == 403


def test_student_not_enrolled_gets_400(client, data):
    response = client.post(
        "/api/progress",
        headers=auth(data["teacher_token"]),
        json=progress_payload(data, student_id=data["outsider_id"]),
    )
    assert response.status_code == 400


def test_student_reads_own_progress(client, data):
    client.post("/api/progress", headers=auth(data["teacher_token"]), json=progress_payload(data))
    response = client.get(
        f"/api/progress/students/{data['student_id']}",
        headers=auth(data["student_token"]),
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_student_cannot_read_other_progress(client, data):
    response = client.get(
        f"/api/progress/students/{data['outsider_id']}",
        headers=auth(data["student_token"]),
    )
    assert response.status_code == 403


def test_staff_reads_any_progress(client, data):
    client.post("/api/progress", headers=auth(data["teacher_token"]), json=progress_payload(data))
    response = client.get(
        f"/api/progress/students/{data['student_id']}",
        headers=auth(data["staff_token"]),
    )
    assert response.status_code == 200
    assert len(response.json()) == 1