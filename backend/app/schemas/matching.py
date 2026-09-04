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

    semantic_score: float = Field(
        ge=0,
        le=100,
    )

    matched_skills: list[str] = Field(
        default_factory=list
    )

    missing_skills: list[str] = Field(
        default_factory=list
    )

    experience_status: str

    match_level: str

    explanation: str

    class Config:
        from_attributes = True


class JobMatchListResponse(BaseModel):
    job_id: int
    total_matches: int

    matches: list[JobMatchResponse]