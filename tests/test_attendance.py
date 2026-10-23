import pytest

from helpers import auth


def attendance_url(session_id):
    return f"/api/sessions/{session_id}/attendance"


@pytest.fixture
def data(client, make_user):
    staff_token, _ = make_user("staff.att@example.com", role="staff")
    teacher_token, teacher_id = make_user("prof.att@example.com", role="teacher")
    other_token, _ = make_user("prof2.att@example.com", role="teacher")
    student_token, student_id = make_user("eleve.att@example.com", level="debutant")
    _, outsider_id = make_user("outsider.att@example.com")

    course = client.post(
        "/api/courses",
        headers=auth(staff_token),
        json={
            "teacher_id": teacher_id,
            "title": "Maths",
            "subject": "Mathématiques",
            "day_of_week": 6,
            "level": "debutant",
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
