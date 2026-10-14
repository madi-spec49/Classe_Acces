from fastapi import FastAPI

from app.config import engine
from app.models import Base
from app.routes import auth, staff, courses, registrations

app = FastAPI(title="My FastAPI Application")

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(staff.router)
app.include_router(courses.router)
app.include_router(registrations.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
