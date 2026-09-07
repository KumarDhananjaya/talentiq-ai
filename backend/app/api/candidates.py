from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.candidate import Candidate
from app.schemas.candidate import (
    CandidateCreate,
    CandidateResponse,
    CandidateUpdate,
    
)
from app.services.resume_parser import (
    extract_text_from_pdf,
    parse_resume,
)
from app.services.candidate_service import (
    create_candidate,
    get_candidate,
    get_candidates,
    update_candidate,
    delete_candidate
)
from app.services.llm_resume_parser import (
    extract_resume_with_llm,
)

from app.services.resume_merge_service import (
    merge_resume_results,
)

from app.services.candidate_search_service import (
    search_candidates,
)
from app.models.candidate_experience import CandidateExperience
from app.services.embedding_service import generate_embedding
from app.services.match_invalidation_service import invalidate_candidate_matches
from app.services.profile_text_service import build_candidate_profile


router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"],
)

UPLOAD_DIR = Path("uploads/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Note: If you want DOCX support later, you must add an extract_text_from_docx function.
ALLOWED_EXTENSIONS = {".pdf"} 

MAX_FILE_SIZE = 5 * 1024 * 1024

@router.post("/", response_model=CandidateResponse)
def create_candidate_endpoint(
    candidate: CandidateCreate,
    db: Session = Depends(get_db),
):
    return create_candidate(db=db, candidate=candidate)


@router.get("/", response_model=list[CandidateResponse])
def get_candidates_endpoint(
    db: Session = Depends(get_db),
):
    return get_candidates(db=db)

@router.put(
    "/{candidate_id}",
    response_model=CandidateResponse,
)
def update_candidate_endpoint(
    candidate_id: int,
    candidate: CandidateUpdate,
    db: Session = Depends(get_db),
):
    return update_candidate(
        db=db,
        candidate_id=candidate_id,
        candidate=candidate,
    )

@router.delete(
    "/{candidate_id}",
    status_code=204,
)
def delete_candidate_endpoint(
    candidate_id: int,
    db: Session = Depends(get_db),
):
    return delete_candidate(
        db=db,
        candidate_id=candidate_id,
    )

@router.get(
    "/search",
    response_model=list[CandidateResponse],
)
def search_candidates_endpoint(
    skills: str | None = Query(
        default=None,
    ),
    minimum_experience: float | None = Query(
        default=None,
        ge=0,
    ),
    db: Session = Depends(get_db),
):
    """
    Search candidates using skills
    and minimum experience.
    """

    parsed_skills = None

    if skills:
        parsed_skills = [
            skill.strip()
            for skill in skills.split(",")
            if skill.strip()
        ]

    return search_candidates(
        db=db,
        skills=parsed_skills,
        minimum_experience=minimum_experience,
    )


@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate_endpoint(
    candidate_id: int,
    db: Session = Depends(get_db),
):
    return get_candidate(db=db, candidate_id=candidate_id)


@router.post("/{candidate_id}/resume")
async def upload_resume(
    candidate_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # ---------------------------------------------------------
    # Find candidate
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # Validate filename
    # ---------------------------------------------------------
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Only PDF files are allowed. "
                f"Received: {extension}"
            ),
        )

    # ---------------------------------------------------------
    # Read and validate file size
    # ---------------------------------------------------------
    file_content = await file.read()

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Resume must be smaller than 5 MB",
        )

    # ---------------------------------------------------------
    # Store uploaded file
    # ---------------------------------------------------------
    safe_filename = f"{uuid4()}{extension}"
    file_path = UPLOAD_DIR / safe_filename

    file_path.write_bytes(file_content)

    # ---------------------------------------------------------
    # Process resume
    # ---------------------------------------------------------
    try:

        # Step 1: Extract raw text from PDF
        resume_text = extract_text_from_pdf(
            str(file_path)
        )

        # Step 2: Rule-based parsing
        rule_resume = parse_resume(
            resume_text
        )

        # Step 3: Gemini structured extraction
        try:
            llm_resume = extract_resume_with_llm(
                resume_text
            )

        except Exception:
            # LLM failure should not prevent upload.
            # Rule-based extraction will still be used.
            llm_resume = None

        # Step 4: Merge parser results
        merged_resume = merge_resume_results(
            rule_resume=rule_resume,
            llm_resume=llm_resume,
        )

    except Exception as e:

        # Delete uploaded file if processing fails
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=422,
            detail=(
                "Failed to process the resume document: "
                f"{str(e)}"
            ),
        )

    # ---------------------------------------------------------
    # Update raw resume text
    # ---------------------------------------------------------
    candidate.resume_text = resume_text

    # ---------------------------------------------------------
    # Update candidate name
    # ---------------------------------------------------------
    if merged_resume.name:
        candidate.full_name = merged_resume.name

    # ---------------------------------------------------------
    # Update candidate email
    # ---------------------------------------------------------
    if merged_resume.email:

        existing_candidate = (
            db.query(Candidate)
            .filter(
                Candidate.email
                == str(merged_resume.email),
                Candidate.id != candidate_id,
            )
            .first()
        )

        if existing_candidate:
            db.rollback()

            if file_path.exists():
                file_path.unlink()

            raise HTTPException(
                status_code=400,
                detail=(
                    "Candidate with this email "
                    "already exists"
                ),
            )

        candidate.email = str(
            merged_resume.email
        )

    # ---------------------------------------------------------
    # Update candidate phone
    # ---------------------------------------------------------
    if merged_resume.phone:
        candidate.phone = (
            merged_resume.phone
        )

    # ---------------------------------------------------------
    # Update candidate skills
    # ---------------------------------------------------------
    if merged_resume.skills:
        candidate.skills = (
            merged_resume.skills
        )

    # ---------------------------------------------------------
    # Update total experience
    # ---------------------------------------------------------
    candidate.experience_years = (
        rule_resume.total_experience_years
    )

    # ---------------------------------------------------------
    # Synchronize candidate experiences
    # ---------------------------------------------------------
    candidate.experiences.clear()

    for experience in merged_resume.experience:

        db_experience = CandidateExperience(
            company=experience.company,
            role=experience.role,
            start_date=experience.start_date,
            end_date=experience.end_date,
            is_current=experience.is_current,
            description=experience.description,
        )

        candidate.experiences.append(
            db_experience
        )

    # ---------------------------------------------------------
    # Rebuild candidate profile
    # ---------------------------------------------------------
    candidate_profile = build_candidate_profile(
        candidate
    )

    # ---------------------------------------------------------
    # Regenerate candidate embedding
    # ---------------------------------------------------------
    candidate.embedding = generate_embedding(
        candidate_profile
    )

    # ---------------------------------------------------------
    # Invalidate old persisted matches
    #
    # Skills, experience and embedding may have changed,
    # so previously calculated matches are no longer valid.
    # ---------------------------------------------------------
    invalidate_candidate_matches(
        db=db,
        candidate_id=candidate.id,
    )

    # ---------------------------------------------------------
    # Persist all candidate changes atomically
    # ---------------------------------------------------------
    try:

        db.commit()
        db.refresh(candidate)

    except Exception:

        db.rollback()

        if file_path.exists():
            file_path.unlink()

        raise

    return {
        "message": (
            "Resume uploaded and analyzed successfully"
        ),
        "candidate_id": candidate_id,
        "original_filename": file.filename,
        "stored_filename": safe_filename,
        "file_size": len(file_content),
        "content_type": file.content_type,
        "parsed_resume": (
            merged_resume.model_dump()
        ),
    }