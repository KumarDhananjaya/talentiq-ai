from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.candidates import router as candidates_router
from app.api.jobs import router as jobs_router
from app.database.database import Base, engine

import app.models


app = FastAPI(
    title="TalentIQ AI",
    description="AI-Powered Recruitment Intelligence Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
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