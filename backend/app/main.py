from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.candidates import router as candidates_router
from app.api.jobs import router as jobs_router
from app.database.database import Base, engine
from app.core.config import settings


app = FastAPI(
    title="TalentIQ AI",
    description="AI-Powered Recruitment Intelligence Platform",
    version="1.0.0",
)

cors_origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(
    bind=engine
)


@app.get("/")
def root():
    return {
        "message": "TalentIQ AI API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


app.include_router(candidates_router)
app.include_router(jobs_router)