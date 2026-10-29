import pytest

from helpers import auth


def progress_payload(data, student_id=None):
    return {
        "student_id": student_id or data["student_id"],
        "course_id": data["course_id"],
        "level": "Niveau 2",
        "note": "Bon travail",
    }


@pytest.fixture
def data(client, make_user):
    staff_token, _ = make_user("staff.prog@example.com", role="staff")
    teacher_token, teacher_id = make_user("prof.prog@example.com", role="teacher")
    student_token, student_id = make_user("eleve.prog@example.com", level="debutant")
    _, outsider_id = make_user("outsider.prog@example.com")

    course = client.post(
        "/api/courses",
        headers=auth(staff_token),
        json={
            "teacher_id": teacher_id,
            "title": "Français",
            "subject": "Français",
            "day_of_week": 6,
            "level": "debutant",
            "start_time": "10:00",
            "end_time": "12:00",
            "zoom_link": "https://zoom.example.com/fr",
        },
    ).json()

    return {
        "staff_token": staff_token,
        "teacher_token": teacher_token,
        "student_token": student_token,
        "student_id": student_id,
        "outsider_id": outsider_id,
        "course_id": course["id"],
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
    assert response.json()[0]["course_subject"]
    assert response.json()[0]["course_title"]


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
