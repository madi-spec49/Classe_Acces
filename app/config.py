"""Configuration de la base de données : URL de connexion, moteur et fabrique de sessions."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://school:school_dev_password@localhost:5432/school_assoc")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dépendance FastAPI : fournit une session de base par requête, puis la ferme."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
