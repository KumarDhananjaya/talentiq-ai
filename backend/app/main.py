import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.candidates import router as candidates_router
from app.api.jobs import router as jobs_router
from app.core.config import settings

logger = logging.getLogger(__name__)

app = FastAPI(
    title="TalentIQ AI",
    description="AI-Powered Recruitment Intelligence Platform",
    version="1.0.0",
)

# Parse configured origins and ensure standard local dev origins are always permitted
configured_origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]
default_dev_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
cors_origins = list(set(configured_origins + default_dev_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error on {request.method} {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"},
    )


@app.get("/")
def root():
    return {
        "message": "TalentIQ AI API is running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }


app.include_router(candidates_router)
app.include_router(jobs_router)