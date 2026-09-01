from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.candidate import Candidate
from app.schemas.candidate import (
    CandidateCreate,
    CandidateResponse,
)
from app.services.resume_parser import (
    extract_text_from_pdf,
    parse_resume,
)
from app.services.candidate_service import (
    create_candidate,
    get_candidate,
    get_candidates,
)
from app.services.llm_resume_parser import (
    extract_resume_with_llm,
)

from app.services.resume_merge_service import (
    merge_resume_results,
)


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
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Only PDF files are allowed. Received: {extension}",
        )

    file_content = await file.read()

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Resume must be smaller than 5 MB",
        )

    safe_filename = f"{uuid4()}{extension}"
    file_path = UPLOAD_DIR / safe_filename

    # Safely write the file (blocks minimally, but for true async use aiofiles)
    file_path.write_bytes(file_content)

    # ---------------------------------------------------------
    # FIX: Wrap parsing in try/except to catch corrupted PDFs
    # ---------------------------------------------------------
    try:
    # ---------------------------------------------------------
    # Step 1: Extract raw text from PDF
    # ---------------------------------------------------------
        resume_text = extract_text_from_pdf(
            str(file_path)
        )

        # ---------------------------------------------------------
        # Step 2: Rule-based parsing
        # ---------------------------------------------------------
        rule_resume = parse_resume(
            resume_text
        )

        # ---------------------------------------------------------
        # Step 3: Gemini structured extraction
        # ---------------------------------------------------------
        try:
            llm_resume = extract_resume_with_llm(
                resume_text
            )

        except Exception:
            # LLM failure should not break resume upload.
            # The merge service will fall back to rule-based data.
            llm_resume = None

        # ---------------------------------------------------------
        # Step 4: Merge both parser results
        # ---------------------------------------------------------
        merged_resume = merge_resume_results(
            rule_resume=rule_resume,
            llm_resume=llm_resume,
        )

    except Exception as e:
        # Delete uploaded file if document processing fails
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=422,
            detail=(
                "Failed to process the resume document: "
                f"{str(e)}"
            ),
     )

    # Save raw text to database
    # ---------------------------------------------------------
    #   Save raw resume text
    # ---------------------------------------------------------
    candidate.resume_text = resume_text


    # ---------------------------------------------------------
    # Update candidate fields using merged extraction
    # ---------------------------------------------------------
    if merged_resume.name:
        candidate.full_name = merged_resume.name

    if merged_resume.email:
        candidate.email = merged_resume.email

    if merged_resume.phone:
        candidate.phone = merged_resume.phone


    # ---------------------------------------------------------
    # Save merged skills
    # ---------------------------------------------------------
    if merged_resume.skills:
        candidate.skills = ", ".join(
            merged_resume.skills
        )


    # ---------------------------------------------------------
    # Keep rule-based experience calculation
    # ---------------------------------------------------------
    candidate.experience_years = (
        rule_resume.total_experience_years
    )

    
    db.commit()
    db.refresh(candidate)

    return {
       "message": "Resume uploaded and analyzed successfully",
        "candidate_id": candidate_id,
        "original_filename": file.filename,
        "stored_filename": safe_filename,
        "file_size": len(file_content),
        "content_type": file.content_type,
        "parsed_resume": merged_resume.model_dump(),
    }