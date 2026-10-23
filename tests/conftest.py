"""Fixtures partagées par toute la suite de tests.

Les tests tournent sur une base SQLite en mémoire : les tables sont créées
avant chaque test et supprimées après. Les comptes ne passent pas par une
route d'inscription (elle n'existe pas) : la fixture `make_user` les insère
directement en base, puis génère un token JWT valide pour eux.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import get_db
from app.main import app
from app.models import Base, User
from app.security import create_access_token, hash_password

from helpers import PASSWORD


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def make_user(client):
    """Crée un utilisateur en base et renvoie (token, id).

    Dépend de `client` pour que les tables existent avant l'insertion.
    """

    def _make(email, role="student", level=None):
        db = TestingSessionLocal()
        try:
            user = User(
                email=email,
                password_hash=hash_password(PASSWORD),
                role=role,
                level=level,
                first_name="Test",
                last_name="User",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return create_access_token(user.id, user.email), user.id
        finally:
            db.close()

    return _make
