import pytest

from helpers import auth


def course_payload(teacher_id, start="10:00:00", end="11:30:00", level="debutant"):
    return {
        "teacher_id": teacher_id,
        "title": "Mathématiques",
        "subject": "Mathématiques",
        "day_of_week": 6,
        "start_time": start,
        "end_time": end,
        "zoom_link": "https://zoom.us/j/123456789",
        "level": level,
    }


def session_payload():
    return {"date": "2026-10-18T10:00:00", "zoom_link": "https://zoom.us/j/123456789"}


@pytest.fixture
def staff_token(make_user):
    token, _ = make_user("staff@example.com", role="staff")
    return token


@pytest.fixture
def student_token(make_user):
    token, _ = make_user("eleve@example.com", role="student", level="debutant")
    return token


@pytest.fixture
def teacher_id(make_user):
    _, teacher_id = make_user("prof@example.com", role="teacher")
    return teacher_id


def create_course(client, staff_token, teacher_id, level="debutant"):
    response = client.post(
        "/api/courses",
        json=course_payload(teacher_id, level=level),
        headers=auth(staff_token),
    )
    return response.json()["id"]


def test_staff_can_create_course(client, staff_token, teacher_id):
    response = client.post(
        "/api/courses",
        json=course_payload(teacher_id),
        headers=auth(staff_token),
    )

    assert response.status_code == 200
    assert response.json()["teacher_id"] == teacher_id


def test_student_cannot_create_course(client, student_token, teacher_id):
    response = client.post(
        "/api/courses",
        json=course_payload(teacher_id),
        headers=auth(student_token),
    )

    assert response.status_code == 403


def test_course_teacher_must_be_a_teacher(client, make_user, staff_token):
    _, student_id = make_user("autre-eleve@example.com", role="student")

    response = client.post(
        "/api/courses",
        json=course_payload(student_id),
        headers=auth(staff_token),
    )

    assert response.status_code == 400


def test_end_time_before_start_time_returns_422(client, staff_token, teacher_id):
    response = client.post(
        "/api/courses",
        json=course_payload(teacher_id, start="11:00:00", end="10:00:00"),
        headers=auth(staff_token),
    )

    assert response.status_code == 422


def test_student_can_list_courses_of_own_level(client, staff_token, student_token, teacher_id):
    create_course(client, staff_token, teacher_id, level="debutant")
    create_course(client, staff_token, teacher_id, level="avance")

    response = client.get("/api/courses", headers=auth(student_token))

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["level"] == "debutant"


def test_staff_can_create_session(client, staff_token, teacher_id):
    course_id = create_course(client, staff_token, teacher_id)

    response = client.post(
        f"/api/courses/{course_id}/sessions",
        json=session_payload(),
        headers=auth(staff_token),
    )

    assert response.status_code == 200
    assert response.json()["course_id"] == course_id


def test_student_cannot_create_session(client, staff_token, student_token, teacher_id):
    course_id = create_course(client, staff_token, teacher_id)

    response = client.post(
        f"/api/courses/{course_id}/sessions",
        json=session_payload(),
        headers=auth(student_token),
    )

    assert response.status_code == 403


def test_session_on_unknown_course_returns_404(client, staff_token):
    response = client.post(
        "/api/courses/999/sessions",
        json=session_payload(),
        headers=auth(staff_token),
    )

    assert response.status_code == 404


def test_student_can_list_sessions(client, staff_token, student_token, teacher_id):
    course_id = create_course(client, staff_token, teacher_id)
    client.post(
        f"/api/courses/{course_id}/sessions",
        json=session_payload(),
        headers=auth(staff_token),
    )

    response = client.get(
        f"/api/courses/{course_id}/sessions",
        headers=auth(student_token),
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_teacher_can_delete_own_course(client, make_user, staff_token):
    teacher_token, teacher_id = make_user("prof.suppr@example.com", role="teacher")
    course_id = create_course(client, staff_token, teacher_id)

    response = client.delete(f"/api/courses/{course_id}", headers=auth(teacher_token))

    assert response.status_code == 200
    remaining = client.get("/api/courses", headers=auth(staff_token)).json()
    assert course_id not in [c["id"] for c in remaining]


def test_other_teacher_cannot_delete_course(client, make_user, staff_token, teacher_id):
    course_id = create_course(client, staff_token, teacher_id)
    other_token, _ = make_user("prof.autre@example.com", role="teacher")

    response = client.delete(f"/api/courses/{course_id}", headers=auth(other_token))

    assert response.status_code == 403


def test_student_cannot_delete_course(client, staff_token, student_token, teacher_id):
    course_id = create_course(client, staff_token, teacher_id)

    response = client.delete(f"/api/courses/{course_id}", headers=auth(student_token))

    assert response.status_code == 403


def test_staff_can_delete_any_course(client, staff_token, teacher_id):
    course_id = create_course(client, staff_token, teacher_id)

    response = client.delete(f"/api/courses/{course_id}", headers=auth(staff_token))

    assert response.status_code == 200


def test_delete_unknown_course_returns_404(client, staff_token):
    response = client.delete("/api/courses/999", headers=auth(staff_token))

    assert response.status_code == 404
