from app.schemas.resume import ParsedResume
from app.schemas.resume_extraction import (
    EducationItem,
    ExperienceItem,
    ResumeExtraction,
)


def _merge_skills(
    rule_skills: list[str],
    llm_skills: list[str],
) -> list[str]:
    """
    Combine skills from both parsers while removing duplicates
    case-insensitively.
    """

    merged: list[str] = []
    seen: set[str] = set()

    for skill in rule_skills + llm_skills:
        normalized = skill.strip()

        if not normalized:
            continue

        key = normalized.lower()

        if key not in seen:
            seen.add(key)
            merged.append(normalized)

    return merged


def _merge_experience(
    rule_resume: ParsedResume,
    llm_resume: ResumeExtraction,
) -> list[ExperienceItem]:
    """
    Prefer the structured LLM experience.

    If Gemini does not extract experience, fall back to
    rule-based experience entries.
    """

    if llm_resume.experience:
        return llm_resume.experience

    return [
        ExperienceItem(
            company=experience.company,
            role=experience.role,
            start_date=None,
            end_date=None,
            is_current=False,
            description=[],
        )
        for experience in rule_resume.experience
    ]


def _merge_education(
    rule_resume: ParsedResume,
    llm_resume: ResumeExtraction,
) -> list[EducationItem]:
    """
    Prefer LLM education because it contains more structured fields.

    Fall back to rule-based education if the LLM returns nothing.
    """

    if llm_resume.education:
        return llm_resume.education

    return [
        EducationItem(
            institution=education.institution,
            degree=education.degree,
            field_of_study=None,
            start_year=None,
            end_year=None,
        )
        for education in rule_resume.education
    ]


def merge_resume_results(
    rule_resume: ParsedResume,
    llm_resume: ResumeExtraction | None,
) -> ResumeExtraction:
    """
    Merge rule-based and LLM resume extraction results.

    Priority rules:

    - Name: rule-based -> LLM fallback
    - Email: rule-based -> LLM fallback
    - Phone: rule-based -> LLM fallback
    - Location: LLM -> rule-based fallback
    - Skills: combine both
    - Experience: LLM -> rule-based fallback
    - Education: LLM -> rule-based fallback
    - Projects: LLM only
    - Certifications: LLM only
    - Languages: LLM only

    If the LLM extraction fails, the rule-based result is still
    converted into the unified ResumeExtraction format.
    """

    if llm_resume is None:
        return ResumeExtraction(
            name=rule_resume.full_name,
            email=rule_resume.email,
            phone=rule_resume.phone,
            location=rule_resume.location,
            skills=_merge_skills(
                rule_resume.skills,
                [],
            ),
            experience=_merge_experience(
                rule_resume,
                ResumeExtraction(),
            ),
            education=_merge_education(
                rule_resume,
                ResumeExtraction(),
            ),
        )

    return ResumeExtraction(
        name=rule_resume.full_name or llm_resume.name,
        email=rule_resume.email or llm_resume.email,
        phone=rule_resume.phone or llm_resume.phone,
        location=llm_resume.location or rule_resume.location,
        skills=_merge_skills(
            rule_resume.skills,
            llm_resume.skills,
        ),
        experience=_merge_experience(
            rule_resume,
            llm_resume,
        ),
        education=_merge_education(
            rule_resume,
            llm_resume,
        ),
        projects=llm_resume.projects,
        certifications=llm_resume.certifications,
        languages=llm_resume.languages,
    )