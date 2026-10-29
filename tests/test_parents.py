import pytest

from helpers import PASSWORD, auth


def login(client, email):
    response = client.post("/api/auth/login", json={"email": email, "password": PASSWORD})
    return response.json()["access_token"]


def make_parent(client, staff_token, email):
    """Crée un parent via la route staff, puis le connecte."""
    response = client.post(
        "/api/parents",
        headers=auth(staff_token),
        json={"email": email, "password": PASSWORD, "first_name": "Parent", "last_name": "Test"},
    )
    return login(client, email), response.json()["id"]


@pytest.fixture
def data(client, make_user):
    staff_token, _ = make_user("staff.par@example.com", role="staff")
    student_token, student_id = make_user("eleve.par@example.com", level="debutant")
    parent_token, parent_id = make_parent(client, staff_token, "parent.par@example.com")
    other_parent_token, _ = make_parent(client, staff_token, "parent2.par@example.com")

    return {
        "staff_token": staff_token,
        "student_token": student_token,
        "student_id": student_id,
        "parent_token": parent_token,
        "parent_id": parent_id,
        "other_parent_token": other_parent_token,
    }


def test_staff_creates_parent(client, data):
    response = client.post(
        "/api/parents",
        headers=auth(data["staff_token"]),
        json={"email": "parent3.par@example.com", "password": PASSWORD, "first_name": "Nouveau", "last_name": "Parent"},
    )

    assert response.status_code == 200
    assert response.json()["role"] == "parent"


def test_student_cannot_create_parent(client, data):
    response = client.post(
        "/api/parents",
        headers=auth(data["student_token"]),
        json={"email": "parent4.par@example.com", "password": PASSWORD, "first_name": "Non", "last_name": "Autorise"},
    )

    assert response.status_code == 403


def test_staff_links_parent_to_student(client, data):
    response = client.post(
        f"/api/parents/{data['parent_id']}/students/{data['student_id']}",
        headers=auth(data["staff_token"]),
    )

    assert response.status_code == 200


def test_linked_parent_reads_student_progress(client, data):
    client.post(
        f"/api/parents/{data['parent_id']}/students/{data['student_id']}",
        headers=auth(data["staff_token"]),
    )

    response = client.get(
        f"/api/progress/students/{data['student_id']}",
        headers=auth(data["parent_token"]),
    )

    assert response.status_code == 200
    assert response.json() == []


def test_unlinked_parent_cannot_read_progress(client, data):
    response = client.get(
        f"/api/progress/students/{data['student_id']}",
        headers=auth(data["other_parent_token"]),
    )

    assert response.status_code == 403


def test_parent_cannot_list_courses(client, data):
    response = client.get("/api/courses", headers=auth(data["parent_token"]))

    assert response.status_code == 403


def test_parent_cannot_list_sessions(client, make_user, data):
    _, teacher_id = make_user("prof.par@example.com", role="teacher")
    course = client.post(
        "/api/courses",
        headers=auth(data["staff_token"]),
        json={
            "teacher_id": teacher_id,
            "title": "Maths",
            "subject": "Maths",
            "day_of_week": 6,
            "start_time": "10:00:00",
            "end_time": "11:00:00",
            "level": "debutant",
        },
    ).json()

    response = client.get(
        f"/api/courses/{course['id']}/sessions",
        headers=auth(data["parent_token"]),
    )

    assert response.status_code == 403


def test_link_unknown_student_returns_404(client, data):
    response = client.post(
        f"/api/parents/{data['parent_id']}/students/9999",
        headers=auth(data["staff_token"]),
    )

    assert response.status_code == 404
