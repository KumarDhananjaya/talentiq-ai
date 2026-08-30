import re
from datetime import datetime
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
from pypdf import PdfReader

from app.database.database import get_db
from app.models.candidate import Candidate
from app.schemas.candidate import (
    CandidateCreate,
    CandidateResponse,
)
from app.schemas.resume import (
    EducationItem,
    ExperienceItem,
    ParsedResume,
)

SKILL_DICTIONARY = [
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C", 
    "React", "Next.js", "Node.js", "Express.js", "FastAPI", 
    "Django", "Flask", "Machine Learning", "Deep Learning", 
    "TensorFlow", "PyTorch", "scikit-learn", "SQL", "PostgreSQL", 
    "MySQL", "MongoDB", "Docker", "Kubernetes", "AWS", "Azure", 
    "Git", "GitHub", "GitHub Actions", "Pandas", "NumPy", 
    "XGBoost", "LangChain", "LLM", "Large Language Models", 
    "Generative AI", "OpenAI",
]


def normalize_pdf_text(text: str) -> str:
    """
    Fix garbled text caused by PDF font subset encoding issues.

    Some PDFs (especially those exported from design tools) use a private-use
    font subset where digits 0-9 are remapped to punctuation/symbol glyphs.

    Observed mapping for this PDF's font:
        ! -> 2,  " -> 0,  # -> 3,  $ -> 4,  % -> 5,  & -> 2,  ' -> 4

    Substitution is applied selectively to tokens that are likely garbled numbers:
      - Tokens that are purely glyph/digit (e.g. years, phone fragments)
      - Tokens that contain '@' (email local parts like "kumar6&.shivu@gmail.com")
      - Tokens where digits + glyphs make up the majority (e.g. "8.6$/4$")
    """
    GLYPH_MAP = str.maketrans({
        "!": "2", '"': "0", "#": "3", "$": "4",
        "%": "5", "&": "2", "'": "4", "\u2019": "4",
    })

    GLYPH_CHARS = set('!"#$%&\'\u2019')
    GLYPH_PATTERN = re.compile(r'[!"#$%&\'\u2019]')

    lines = []
    for line in text.splitlines():
        tokens = line.split()
        fixed_tokens = []
        for token in tokens:
            if not GLYPH_PATTERN.search(token):
                fixed_tokens.append(token)
                continue

            alpha_chars = sum(1 for c in token if c.isalpha())
            glyph_chars = sum(1 for c in token if c in GLYPH_CHARS)
            digit_chars = sum(1 for c in token if c.isdigit())

            # Always normalize tokens that contain an email '@'
            if "@" in token:
                fixed_tokens.append(token.translate(GLYPH_MAP))
            # Pure glyph/digit tokens (years, version numbers, phone fragments)
            elif alpha_chars == 0:
                fixed_tokens.append(token.translate(GLYPH_MAP))
            # Mixed but glyphs outnumber or equal alpha chars (garbled section headers etc.)
            elif glyph_chars >= alpha_chars:
                fixed_tokens.append(token.translate(GLYPH_MAP))
            # Tokens where digits + glyphs together outnumber alpha (e.g. "8.62/42")
            elif (glyph_chars + digit_chars) > alpha_chars:
                fixed_tokens.append(token.translate(GLYPH_MAP))
            else:
                fixed_tokens.append(token)
        lines.append(" ".join(fixed_tokens))

    return "\n".join(lines)


def extract_text_from_pdf(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Resume file not found: {file_path}")

    raw_text = ""

    # Try PyMuPDF first (better layout preservation)
    try:
        import pymupdf  # type: ignore
        doc = pymupdf.open(str(path))
        pages = [page.get_text() for page in doc]
        raw_text = "\n".join(pages).strip()
    except ImportError:
        pass

    # Fall back to pypdf
    if not raw_text:
        reader = PdfReader(path)
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        raw_text = "\n".join(pages).strip()

    return normalize_pdf_text(raw_text)


def extract_email(text: str) -> str | None:
    """
    Extract email from (potentially garbled) PDF text.

    Strategy:
    1. First try a standard strict regex on the full text (fast path for clean PDFs).
    2. If that fails, locate the '@' token, collect surrounding words (to handle
       spaces inserted by PDF extraction), join them, then apply a broader regex
       that tolerates residual garbled chars in the local part.
    3. After matching, sanitize the local part by applying the same glyph->digit
       normalization so we never return something like "kumar6&.shivu@gmail.com".
    """
    if "@" not in text:
        return None

    # Glyph -> digit map for post-match sanitization of any residual mangled chars
    _GLYPH_MAP = str.maketrans({
        "!": "2", '"': "0", "#": "3", "$": "4",
        "%": "5", "&": "2", "'": "4", "\u2019": "4",
    })

    STRICT_PATTERN = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    # Broader: allows garbled digit chars in the local part before @
    BROAD_PATTERN = re.compile(r'[A-Za-z0-9._%+\-!"#$&\'\u2019]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')

    # Fast path — strict match on clean/normalized text
    m = STRICT_PATTERN.search(text)
    if m:
        return m.group(0)

    # Slow path — look for '@' token, widen context, apply broad regex
    words = text.split()
    for i, word in enumerate(words):
        if "@" in word:
            start = max(0, i - 2)
            end = min(len(words), i + 3)
            context = "".join(words[start:end])

            m = BROAD_PATTERN.search(context)
            if m:
                email = m.group(0)
                local, _, domain = email.partition("@")
                local = local.translate(_GLYPH_MAP)
                return f"{local}@{domain}"

    return None


def extract_phone(text: str) -> str | None:
    pattern = r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}[\s.-]?\d{0,4}"
    matches = re.finditer(pattern, text)
    for match in matches:
        phone = match.group(0).strip()
        digits = re.sub(r"\D", "", phone)
        if 9 <= len(digits) <= 15:
            return phone
    return None


def extract_skills(text: str) -> list[str]:
    detected_skills = []
    for skill in SKILL_DICTIONARY:
        flags = 0 if len(skill) <= 2 else re.IGNORECASE
        pattern = r"(?<![a-zA-Z0-9+#.-])" + re.escape(skill) + r"(?![a-zA-Z0-9+#.-])"
        if re.search(pattern, text, flags):
            detected_skills.append(skill)
    return detected_skills


def extract_full_name(text: str) -> str | None:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines[:10]:
        if "@" in line or len(line) < 3 or len(line) > 60:
            continue
        if re.search(r"\d|http|linkedin|github|portfolio", line, re.IGNORECASE):
            continue
        words = line.split()
        if 2 <= len(words) <= 4 and all(word[0].isupper() for word in words if word.isalpha()):
            return re.sub(r"[^\w\s-]", "", line).strip()
    return None


def extract_location(text: str) -> str | None:
    # Explicitly ignores "alt" or garbage prefixes and only extracts the matched City/Region
    pattern = r"(Sydney|Melbourne|Brisbane|Perth|Adelaide|Mysuru|Bangalore|Mysore|New York|London)[\s,]*(NSW|VIC|QLD|WA|SA|TAS|ACT|NT|Australia|India|USA|UK)?"
    match = re.search(pattern, text, re.IGNORECASE)
    
    if match:
        city = match.group(1).title()
        region = match.group(2).title() if match.group(2) else ""
        
        # Keep acronyms fully capitalized
        region_upper = region.upper()
        if region_upper in ["NSW", "VIC", "QLD", "WA", "SA", "TAS", "ACT", "NT", "USA", "UK"]:
            region = region_upper
            
        return f"{city}, {region}" if region else city
    return None


def extract_experience(text: str) -> list[ExperienceItem]:
    experiences = []

    MONTHS = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-zA-Z]*"

    # Standard date tokens (work on clean/normalized text)
    MONTH_YEAR = rf"{MONTHS}\s*\d{{4}}"
    NUM_YEAR = r"\d{1,2}/\d{4}"
    JUST_YEAR = r"(?:19|20)\d{2}"

    # Garbled fallback: "Month <2-6 non-space chars>" — catches PDF-mangled years like "!"!'"
    GARBLED_MONTH_YEAR = rf"{MONTHS}\s+\S{{2,6}}"

    DATE_TERM = f"(?:{MONTH_YEAR}|{NUM_YEAR}|{JUST_YEAR}|{GARBLED_MONTH_YEAR})"

    # Matches: Start Date -> separator (-, –, to) -> End Date (or Present/Current)
    date_pattern = re.compile(
        rf"({DATE_TERM}\s*(?:[-–—|]+|to)\s*(?:Present|Current|Now|{DATE_TERM}))",
        re.IGNORECASE,
    )

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for i, line in enumerate(lines):
        match = date_pattern.search(line)

        if match:
            duration = match.group(0).strip()
            role_line = line.replace(duration, "").strip()

            # If the duration was on its own line, grab role from previous or next line
            if len(role_line) < 5:
                if i > 0 and len(lines[i - 1]) > 4:
                    role_line = lines[i - 1]
                elif i + 1 < len(lines) and len(lines[i + 1]) > 4:
                    role_line = lines[i + 1]

            role_line = re.sub(r"[^a-zA-Z0-9\s,&/|\-]", "", role_line).strip()

            if not role_line or len(role_line) > 100:
                continue

            # Skip single-word non-role lines (e.g. "Expected", "India", "Australia")
            words_in_role = role_line.split()
            if len(words_in_role) < 2:
                continue

            # Skip if it looks like an education line, not a job title
            if re.search(
                r"\b(Bachelor|Master|Doctor|PhD|B\.E\.|B\.Tech|M\.Tech|University|Institute|College|School|CGPA|Expected)\b",
                role_line,
                re.IGNORECASE,
            ):
                continue

            # Prevent duplication of same roles (sometimes multi-line dates trigger twice)
            if experiences and experiences[-1].role == role_line[:80]:
                continue

            experiences.append(
                ExperienceItem(
                    role=role_line[:80],
                    duration=duration,
                )
            )

    return experiences[:10]


def extract_education(text: str) -> list[EducationItem]:
    education = []
    degree_patterns = [
        r"(Master(?:'s)? (?:of|in) [A-Za-z &]+)",
        r"(Bachelor(?:'s)? (?:of|in) [A-Za-z &]+)",
        r"(B\.?E\.?(?:\s+in)?\s+[A-Za-z &]+)",
        r"(B\.?Tech(?:\s+in)?\s+[A-Za-z &]+)",
    ]

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for index, line in enumerate(lines):
        for pattern in degree_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                degree = match.group(1).strip()
                institution = None
                
                start_idx = max(0, index - 2)
                end_idx = min(len(lines), index + 3)

                for j in range(start_idx, end_idx):
                    if j == index and "-" in line:
                        parts = line.split("-")
                        for part in parts:
                            if re.search(r"(University|Institute|College|School)", part, re.IGNORECASE):
                                institution = part.strip()
                    else:
                        if re.search(r"(University|Institute|College|School)", lines[j], re.IGNORECASE):
                            institution = lines[j].strip()
                            break

                if institution:
                    institution = re.sub(r"[^\w\s,&-]", "", institution).strip()

                education.append(EducationItem(degree=degree, institution=institution))
                break

    return education[:5]


def calculate_experience_years(experiences: list[ExperienceItem]) -> float | None:
    if not experiences:
        return None

    total_years = 0.0
    for exp in experiences:
        # Extract all 4-digit years from the duration string
        years = re.findall(r"\b(19\d{2}|20\d{2})\b", exp.duration)
        if not years:
            continue
            
        start_year = int(years[0])
        
        if re.search(r"(present|current|now)", exp.duration, re.IGNORECASE):
            end_year = datetime.now().year
        elif len(years) >= 2:
            end_year = int(years[1])
        else:
            end_year = start_year
            
        diff = end_year - start_year
        if diff == 0:
            total_years += 0.5  # Approximate half a year if started & ended in same year
        elif diff > 0:
            total_years += diff

    return round(total_years, 1) if total_years > 0 else None


def parse_resume(text: str) -> ParsedResume:
    experiences = extract_experience(text)
    return ParsedResume(
        full_name=extract_full_name(text),
        email=extract_email(text),
        phone=extract_phone(text),
        location=extract_location(text),
        skills=extract_skills(text),
        experience=experiences,
        education=extract_education(text),
        total_experience_years=calculate_experience_years(experiences),
    )


# ==========================================
# FASTAPI ROUTER 
# ==========================================

router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"],
)

UPLOAD_DIR = Path("uploads/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE = 5 * 1024 * 1024


@router.post("/", response_model=CandidateResponse)
def create_candidate_endpoint(
    candidate: CandidateCreate,
    db: Session = Depends(get_db),
):
    from app.services.candidate_service import create_candidate
    return create_candidate(db=db, candidate=candidate)


@router.get("/", response_model=list[CandidateResponse])
def get_candidates_endpoint(
    db: Session = Depends(get_db),
):
    from app.services.candidate_service import get_candidates
    return get_candidates(db=db)


@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate_endpoint(
    candidate_id: int,
    db: Session = Depends(get_db),
):
    from app.services.candidate_service import get_candidate
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
            detail="Only PDF and DOCX files are allowed",
        )

    file_content = await file.read()

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Resume must be smaller than 5 MB",
        )

    safe_filename = f"{uuid4()}{extension}"
    file_path = UPLOAD_DIR / safe_filename
    file_path.write_bytes(file_content)

    resume_text = extract_text_from_pdf(str(file_path))

    candidate.resume_text = resume_text
    parsed_resume = parse_resume(resume_text)

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