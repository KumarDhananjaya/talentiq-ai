from typing import Optional

from pydantic import BaseModel, Field


class ExperienceItem(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: list[str] = Field(default_factory=list)


class EducationItem(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None


class ProjectItem(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    technologies: list[str] = Field(default_factory=list)


class CertificationItem(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    year: Optional[int] = None


class ResumeExtraction(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None

    skills: list[str] = Field(default_factory=list)

    experience: list[ExperienceItem] = Field(
        default_factory=list
    )

    education: list[EducationItem] = Field(
        default_factory=list
    )

    projects: list[ProjectItem] = Field(
        default_factory=list
    )

    certifications: list[CertificationItem] = Field(
        default_factory=list
    )

    languages: list[str] = Field(default_factory=list)