from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CandidateExperienceCreate(BaseModel):
    company: str | None = None
    role: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    is_current: bool = False
    description: str | None = None


class CandidateExperienceResponse(
    CandidateExperienceCreate
):
    id: int
    candidate_id: int

    model_config = ConfigDict(
        from_attributes=True
    )


class CandidateCreate(BaseModel):
    full_name: str
    email: EmailStr | None = None
    phone: str | None = None
    resume_text: str | None = None

    skills: list[str] = Field(
        default_factory=list
    )

    experience_years: float | None = None

    experiences: list[
        CandidateExperienceCreate
    ] = Field(
        default_factory=list
    )


class CandidateResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr | None = None
    phone: str | None = None
    resume_text: str | None = None

    skills: list[str] = Field(
        default_factory=list
    )

    experience_years: float | None = None

    created_at: datetime

    experiences: list[
        CandidateExperienceResponse
    ] = Field(
        default_factory=list
    )

    model_config = ConfigDict(
        from_attributes=True
    )