"""Crée un compte staff directement en base.

Il n'existe pas d'inscription publique : le premier compte staff se crée avec
ce script, depuis la machine qui a accès à la base.

    python -m scripts.create_staff
"""

import sys
from getpass import getpass

from pydantic import EmailStr, TypeAdapter, ValidationError
from sqlalchemy.orm import Session

from app.config import SessionLocal, engine
from app.models import Base, User
from app.security import hash_password

MIN_PASSWORD_LENGTH = 8


def create_staff(db: Session, email: str, first_name: str, last_name: str, password: str) -> User:
    """Crée un compte staff, ou lève ValueError si les données sont refusées."""
    try:
        email = str(TypeAdapter(EmailStr).validate_python(email))
    except ValidationError:
        raise ValueError("Email invalide.")

    if not first_name.strip() or not last_name.strip():
        raise ValueError("Le prénom et le nom sont obligatoires.")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Le mot de passe doit faire au moins {MIN_PASSWORD_LENGTH} caractères.")
    if db.query(User).filter(User.email == email).first() is not None:
        raise ValueError("Cet email est déjà utilisé.")

    staff = User(
        email=email,
        password_hash=hash_password(password),
        role="staff",
        first_name=first_name.strip(),
        last_name=last_name.strip(),
    )
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff


def main() -> int:
    email = input("Email : ").strip()
    first_name = input("Prénom : ")
    last_name = input("Nom : ")
    password = getpass("Mot de passe : ")
    if getpass("Confirmer le mot de passe : ") != password:
        print("Les mots de passe ne correspondent pas.")
        return 1

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        staff = create_staff(db, email, first_name, last_name, password)
    except ValueError as error:
        print(error)
        return 1
    finally:
        db.close()

    print(f"Compte staff créé : {staff.email}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
