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


def attendance_url(session_id):
    return f"/api/sessions/{session_id}/attendance"


@pytest.fixture
def data(client):
    staff_token, _ = make_user(client, "staff.att@example.com", "staff")
    teacher_token, teacher_id = make_user(client, "prof.att@example.com", "teacher")
    other_token, _ = make_user(client, "prof2.att@example.com", "teacher")
    student_token, student_id = make_user(client, "eleve.att@example.com")
    _, outsider_id = make_user(client, "outsider.att@example.com")

    course = client.post(
        "/api/courses",
        headers=auth(staff_token),
        json={
            "teacher_id": teacher_id,
            "title": "Maths",
            "subject": "Mathématiques",
            "day_of_week": 6,
            "start_time": "10:00",
            "end_time": "12:00",
            "zoom_link": "https://zoom.example.com/maths",
        },
    ).json()

    session = client.post(
        f"/api/courses/{course['id']}/sessions",
        headers=auth(staff_token),
        json={"date": "2026-10-18T10:00:00Z", "zoom_link": "https://zoom.example.com/maths"},
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
        "other_token": other_token,
        "student_token": student_token,
        "student_id": student_id,
        "outsider_id": outsider_id,
        "session_id": session["id"],
    }


def test_teacher_records_presence(client, data):
    response = client.post(
        attendance_url(data["session_id"]),
        headers=auth(data["teacher_token"]),
        json={"student_id": data["student_id"], "status": "present"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "present"


def test_teacher_updates_existing_record(client, data):
    url = attendance_url(data["session_id"])
    headers = auth(data["teacher_token"])
    first = client.post(url, headers=headers, json={"student_id": data["student_id"], "status": "present"}).json()
    second = client.post(url, headers=headers, json={"student_id": data["student_id"], "status": "late"}).json()
    assert second["id"] == first["id"]
    assert second["status"] == "late"


def test_student_cannot_record_attendance(client, data):
    response = client.post(
        attendance_url(data["session_id"]),
        headers=auth(data["student_token"]),
        json={"student_id": data["student_id"], "status": "present"},
    )
    assert response.status_code == 403


def test_teacher_of_other_course_cannot_record(client, data):
    response = client.post(
        attendance_url(data["session_id"]),
        headers=auth(data["other_token"]),
        json={"student_id": data["student_id"], "status": "present"},
    )
    assert response.status_code == 403


def test_student_not_enrolled_gets_400(client, data):
    response = client.post(
        attendance_url(data["session_id"]),
        headers=auth(data["teacher_token"]),
        json={"student_id": data["outsider_id"], "status": "present"},
    )
    assert response.status_code == 400


def test_staff_can_list_attendance(client, data):
    client.post(
        attendance_url(data["session_id"]),
        headers=auth(data["teacher_token"]),
        json={"student_id": data["student_id"], "status": "present"},
    )
    response = client.get(attendance_url(data["session_id"]), headers=auth(data["staff_token"]))
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_student_cannot_list_attendance(client, data):
    response = client.get(attendance_url(data["session_id"]), headers=auth(data["student_token"]))
    assert response.status_code == 403