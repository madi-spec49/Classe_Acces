import pytest

from conftest import TestingSessionLocal
from app.models import User
from app.security import verify_password
from scripts.create_staff import create_staff


@pytest.fixture
def db(client):
    session = TestingSessionLocal()
    yield session
    session.close()


def test_create_staff_stores_a_hashed_staff_account(db):
    staff = create_staff(db, "admin@example.com", "Ada", "Admin", "motdepasse123")

    saved = db.get(User, staff.id)
    assert saved.role == "staff"
    assert saved.password_hash != "motdepasse123"
    assert verify_password("motdepasse123", saved.password_hash)


def test_created_staff_can_log_in(client, db):
    create_staff(db, "admin@example.com", "Ada", "Admin", "motdepasse123")

    response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "motdepasse123"},
    )

    assert response.status_code == 200
    assert response.json()["user"]["role"] == "staff"


def test_create_staff_refuses_duplicate_email(db):
    create_staff(db, "admin@example.com", "Ada", "Admin", "motdepasse123")

    with pytest.raises(ValueError):
        create_staff(db, "admin@example.com", "Autre", "Admin", "motdepasse123")


def test_create_staff_refuses_short_password(db):
    with pytest.raises(ValueError):
        create_staff(db, "admin@example.com", "Ada", "Admin", "court")


def test_create_staff_refuses_invalid_email(db):
    with pytest.raises(ValueError):
        create_staff(db, "pas-un-email", "Ada", "Admin", "motdepasse123")
