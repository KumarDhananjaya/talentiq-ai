from pydantic import BaseModel, Field


class ExperienceItem(BaseModel):
    role: str | None = None
    company: str | None = None
    duration: str | None = None


class EducationItem(BaseModel):
    degree: str | None = None
    institution: str | None = None


class ParsedResume(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None

    skills: list[str] = Field(default_factory=list)

    experience: list[ExperienceItem] = Field(
        default_factory=list
    )

    education: list[EducationItem] = Field(
        default_factory=list
    )

    total_experience_years: float | None = None