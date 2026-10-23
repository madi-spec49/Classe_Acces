"""Constantes et fonctions utilitaires partagées par les tests."""

PASSWORD = "monMotDePasse123"


def auth(token):
    """Construit le header Authorization à partir d'un token JWT."""
    return {"Authorization": f"Bearer {token}"}
