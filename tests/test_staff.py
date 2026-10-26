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


def test_staff_deletes_student(client, make_user):
    staff_token, _ = make_user("staff.del@example.com", role="staff")
    _, student_id = make_user("eleve.del@example.com", role="student", level="debutant")

    response = client.delete(f"/api/staff/users/{student_id}", headers=auth(staff_token))

    assert response.status_code == 200
    remaining = client.get("/api/staff/users", headers=auth(staff_token)).json()
    assert student_id not in [u["id"] for u in remaining]


def test_staff_deletes_parent(client, make_user):
    staff_token, _ = make_user("staff.delp@example.com", role="staff")
    _, parent_id = make_user("parent.del@example.com", role="parent")

    response = client.delete(f"/api/staff/users/{parent_id}", headers=auth(staff_token))

    assert response.status_code == 200


def test_staff_cannot_delete_teacher_with_courses(client, make_user):
    staff_token, _ = make_user("staff.delt@example.com", role="staff")
    _, teacher_id = make_user("prof.del@example.com", role="teacher")
    client.post(
        "/api/courses",
        json={
            "teacher_id": teacher_id,
            "title": "Cours",
            "subject": "Histoire",
            "day_of_week": 6,
            "start_time": "10:00:00",
            "end_time": "11:00:00",
            "zoom_link": "https://zoom.us/j/1",
            "level": "debutant",
        },
        headers=auth(staff_token),
    )

    response = client.delete(f"/api/staff/users/{teacher_id}", headers=auth(staff_token))

    assert response.status_code == 400


def test_staff_cannot_delete_staff_account(client, make_user):
    staff_token, _ = make_user("staff.delS@example.com", role="staff")
    _, other_staff_id = make_user("staff.autre@example.com", role="staff")

    response = client.delete(f"/api/staff/users/{other_staff_id}", headers=auth(staff_token))

    assert response.status_code == 404


def test_student_cannot_delete_user(client, make_user):
    student_token, _ = make_user("eleve.nodel@example.com", role="student", level="debutant")
    _, other_id = make_user("eleve.cible@example.com", role="student", level="debutant")

    response = client.delete(f"/api/staff/users/{other_id}", headers=auth(student_token))

    assert response.status_code == 403
