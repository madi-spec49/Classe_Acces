"""Point d'entrée de l'API : crée l'application, active CORS et enregistre les routeurs."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import engine
from app.models import Base
from app.routes import auth, staff, courses, attendance, progress, parents, suivi

app = FastAPI(title="Classe Accès API")

# Seul le front-end servi sur le port 5500 peut appeler l'API depuis un navigateur.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crée les tables qui n'existent pas encore (les tables existantes ne sont pas modifiées).
Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(staff.router)
app.include_router(courses.router)
app.include_router(attendance.router)
app.include_router(progress.router)
app.include_router(parents.router)
app.include_router(suivi.router)


@app.get("/health")
def health_check():
    """Route publique qui permet de vérifier que l'API fonctionne."""
    return {"status": "ok"}