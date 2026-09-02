
from app.schemas.candidate import (
    CandidateCreate,
    CandidateExperienceCreate,
)
from app.schemas.resume import ParsedResume


def parsed_resume_to_candidate(
    parsed_resume: ParsedResume,
    resume_text: str,
) -> CandidateCreate:

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