from app.schemas.candidate import (
    CandidateCreate,
    CandidateExperienceCreate,
)
from app.schemas.resume import ParsedResume
from app.schemas.resume_extraction import ResumeExtraction


def parsed_resume_to_candidate(
    parsed_resume: ParsedResume,
    resume_text: str,
) -> CandidateCreate:
    """
    Convert a rule-based ParsedResume into CandidateCreate.

    Kept for backward compatibility and direct
    rule-parser processing.
    """

    experiences = []

    for item in parsed_resume.experience:
        experiences.append(
            CandidateExperienceCreate(
                company=item.company,
                role=item.role,
            )
        )

    return CandidateCreate(
        full_name=(
            parsed_resume.full_name
            or "Unknown Candidate"
        ),
        email=parsed_resume.email,
        phone=parsed_resume.phone,
        resume_text=resume_text,
        skills=parsed_resume.skills,
        experience_years=(
            parsed_resume.total_experience_years
        ),
        experiences=experiences,
    )

def resume_extraction_to_candidate(
    resume: ResumeExtraction,
    resume_text: str,
) -> CandidateCreate:
    """
    Convert the unified merged ResumeExtraction
    into CandidateCreate.
    """

    experiences = []

    for item in resume.experience:
        experiences.append(
            CandidateExperienceCreate(
                company=item.company,
                role=item.role,
                start_date=item.start_date,
                end_date=item.end_date,
                is_current=item.is_current,
                description=(
                    "\n".join(item.description)
                    if item.description
                    else None
                ),
            )
        )

    return CandidateCreate(
        full_name=(
            resume.name
            or "Unknown Candidate"
        ),
        email=resume.email,
        phone=resume.phone,
        resume_text=resume_text,
        skills=resume.skills,
        experiences=experiences,
    )