from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.candidate import Candidate
from app.models.candidate_experience import (
    CandidateExperience,
)
from app.schemas.candidate import (
    CandidateCreate,
    CandidateUpdate,
)
from app.services.profile_text_service import (
    build_candidate_profile,
)

from app.services.embedding_service import (
    generate_embedding,
)

def create_candidate(
    db: Session,
    candidate: CandidateCreate,
) -> Candidate:

    if candidate.email:
        existing_candidate = (
            db.query(Candidate)
            .filter(
                Candidate.email == candidate.email
            )
            .first()
        )

        if existing_candidate:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Candidate with this email "
                    "already exists"
                ),
            )

    db_candidate = Candidate(
        full_name=candidate.full_name,
        email=(
            str(candidate.email)
            if candidate.email
            else None
        ),
        phone=candidate.phone,
        resume_text=candidate.resume_text,
        skills=candidate.skills,
        experience_years=(
            candidate.experience_years
        ),
    )

    # Build candidate profile and generate embedding
    candidate_profile = build_candidate_profile(
        db_candidate
    )

    db_candidate.embedding = generate_embedding(
        candidate_profile
    )

    for experience in candidate.experiences:

        db_experience = CandidateExperience(
            company=experience.company,
            role=experience.role,
            start_date=experience.start_date,
            end_date=experience.end_date,
            is_current=experience.is_current,
            description=experience.description,
        )

        db_candidate.experiences.append(
            db_experience
        )

    try:

        db.add(db_candidate)
        db.commit()
        db.refresh(db_candidate)

    except Exception:

        db.rollback()
        raise

    return db_candidate

def update_candidate(
    db: Session,
    candidate_id: int,
    candidate: CandidateUpdate,
) -> Candidate:

    db_candidate = (
        db.query(Candidate)
        .filter(
            Candidate.id == candidate_id
        )
        .first()
    )

    if not db_candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    update_data = candidate.model_dump(
        exclude_unset=True
    )

    if "email" in update_data:
        new_email = update_data["email"]

        if new_email:
            existing_candidate = (
                db.query(Candidate)
                .filter(
                    Candidate.email == str(new_email),
                    Candidate.id != candidate_id,
                )
                .first()
            )

            if existing_candidate:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Candidate with this email "
                        "already exists"
                    ),
                )

            db_candidate.email = str(new_email)

        else:
            db_candidate.email = None

    if "full_name" in update_data:
        db_candidate.full_name = (
            update_data["full_name"]
        )

    if "phone" in update_data:
        db_candidate.phone = (
            update_data["phone"]
        )

    if "resume_text" in update_data:
        db_candidate.resume_text = (
            update_data["resume_text"]
        )

    if "skills" in update_data:
        db_candidate.skills = (
            update_data["skills"]
        )

    if "experience_years" in update_data:
        db_candidate.experience_years = (
            update_data["experience_years"]
        )

    if "experiences" in update_data:
        db_candidate.experiences.clear()

        for experience in (
            update_data["experiences"] or []
        ):
            db_experience = CandidateExperience(
                company=experience["company"],
                role=experience["role"],
                start_date=experience["start_date"],
                end_date=experience["end_date"],
                is_current=experience["is_current"],
                description=experience["description"],
            )

            db_candidate.experiences.append(
                db_experience
            )

    candidate_profile = build_candidate_profile(
        db_candidate
    )

    db_candidate.embedding = generate_embedding(
        candidate_profile
    )

    try:
        db.commit()
        db.refresh(db_candidate)

    except Exception:
        db.rollback()
        raise

    return db_candidate


def get_candidates(
    db: Session,
) -> list[Candidate]:

    return db.query(Candidate).all()


def get_candidate(
    db: Session,
    candidate_id: int,
) -> Candidate:

    candidate = (
        db.query(Candidate)
        .filter(
            Candidate.id == candidate_id
        )
        .first()
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    return candidate