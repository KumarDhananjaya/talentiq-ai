from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobCreate(BaseModel):
    title: str
    company: str
    description: str
    required_skills: str | None = None
    minimum_experience: int | None = None

class JobUpdate(BaseModel):
    title: str | None = None
    company: str | None = None
    description: str | None = None
    required_skills: str | None = None
    minimum_experience: int | None = None


class JobResponse(JobCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )