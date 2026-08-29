from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class CandidateCreate(BaseModel):
    full_name: str
    email: EmailStr | None = None
    phone: str | None = None
    resume_text: str | None = None
    skills: str | None = None
    experience_years: int | None = None


class CandidateResponse(CandidateCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )