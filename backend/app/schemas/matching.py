from pydantic import BaseModel, Field


class JobMatchResponse(BaseModel):
    candidate_id: int
    job_id: int

    overall_score: float = Field(
        ge=0,
        le=100,
    )

    skill_score: float = Field(
        ge=0,
        le=100,
    )

    experience_score: float = Field(
        ge=0,
        le=100,
    )

    matched_skills: list[str] = Field(
        default_factory=list
    )

    missing_skills: list[str] = Field(
        default_factory=list
    )