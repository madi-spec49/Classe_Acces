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


def make_student(client, email):
    client.post(
        "/api/auth/register",
        json={"email": email, "password": PASSWORD, "first_name": "Test", "last_name": "User"},
    )
    token = login(client, email)
    user_id = client.get("/api/auth/me", headers=auth(token)).json()["id"]
    return token, user_id


def make_parent(client, staff_token, email):
    response = client.post(
        "/api/parents",
        headers=auth(staff_token),
        json={"email": email, "password": PASSWORD, "first_name": "Parent", "last_name": "Test"},
    )
    parent_id = response.json()["id"]
    token = login(client, email)
    return token, parent_id


@pytest.fixture
def data(client):
    client.post(
        "/api/auth/register",
        json={"email": "staff.par@example.com", "password": PASSWORD, "first_name": "Staff", "last_name": "Test"},
    )
    set_role("staff.par@example.com", "staff")
    staff_token = login(client, "staff.par@example.com")

    student_token, student_id = make_student(client, "eleve.par@example.com")
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


def test_link_unknown_student_returns_404(client, data):
    response = client.post(
        f"/api/parents/{data['parent_id']}/students/9999",
        headers=auth(data["staff_token"]),
    )
    assert response.status_code == 404