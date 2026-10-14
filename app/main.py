from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import engine
from app.models import Base
from app.routes import auth, staff, courses, registrations, attendance, progress

app = FastAPI(title="My FastAPI Application")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(staff.router)
app.include_router(courses.router)
app.include_router(registrations.router)
app.include_router(attendance.router)
app.include_router(progress.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}