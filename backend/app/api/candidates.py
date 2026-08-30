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
        # If you add DOCX support later, check `if extension == ".pdf":` here
        resume_text = extract_text_from_pdf(str(file_path))
        
        # Parse the structured data
        parsed_resume = parse_resume(resume_text)
        
    except Exception as e:
        # If parsing fails, delete the corrupted file and return a clean error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=422,
            detail=f"Failed to process the resume document: {str(e)}"
        )

    # Save raw text to database
    candidate.resume_text = resume_text
    
    db.commit()
    db.refresh(candidate)

    return {
        "message": "Resume uploaded and analyzed successfully",
        "candidate_id": candidate_id,
        "original_filename": file.filename,
        "stored_filename": safe_filename,
        "file_size": len(file_content),
        "content_type": file.content_type,
        "parsed_resume": parsed_resume.model_dump(),
    }