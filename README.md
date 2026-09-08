# TalentIQ AI

> **AI-Powered Recruitment Intelligence & Candidate Matching Platform**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.141+-009688.svg?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.2+-61DAFB.svg?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1.svg?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4.0-38B2AC.svg?style=flat-square&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)

TalentIQ AI is an end-to-end recruitment intelligence system designed to automate resume parsing, skill gap analysis, semantic profile vectorization, and candidate-to-job matching with explainable multi-factor scoring.

---

## Key Features

- **Dual-Layer Resume Parsing Pipeline**
  - **Deterministic Extraction**: Extracts contact details, education, dates, and dictionary-matched skills from PDF resumes using PyMuPDF and PyPDF with font glyph normalization for corrupted PDF encodings.
  - **LLM Structured Extraction**: Employs Google Gemini (`gemini-2.5-flash`) via the modern `google-genai` SDK for structured extraction of employment history, responsibilities, projects, and certifications.
  - **Merge Engine**: Intelligently reconciles deterministic and generative outputs with automatic fallback handling.

- **Hybrid Weighted Candidate-Job Matching Engine**
  - Combines structured requirements with semantic vector similarity:
    $$\text{Overall Score} = (0.40 \times \text{Skill Score}) + (0.20 \times \text{Experience Score}) + (0.40 \times \text{Semantic Score})$$
  - **Dense Embeddings**: Generated locally using `sentence-transformers` (`all-MiniLM-L6-v2`) for candidate profiles and job descriptions.
  - **Explainability**: Generates breakdown reports for every match, including matched skills, missing skills, experience status, match level categorization (*Excellent, Strong, Moderate, Weak*), and human-readable summaries.

- **Automated Cache & Match Invalidation**
  - Stale candidate-job matches are automatically invalidated whenever candidate profiles, resumes, or job descriptions are created or updated.

- **Modern Interactive Web Dashboard**
  - Real-time talent analytics and metrics.
  - Candidate management, search, and structured resume uploader.
  - Job management and ranked candidate matches view.

---

## System Architecture

```mermaid
flowchart TD
    subgraph Client["Frontend (React 19 + TypeScript + Vite)"]
        UI[Recruiter Dashboard]
        Upload[Resume Upload & Forms]
        MatchView[Candidate Match Rankings]
    end

    subgraph API["Backend (FastAPI REST API)"]
        CandidatesRouter["/candidates Router"]
        JobsRouter["/jobs Router"]
        
        subgraph Pipeline["Resume Processing Pipeline"]
            PDFParser["PyMuPDF / PyPDF Text Extractor"]
            RuleParser["Deterministic Rule Parser"]
            LLMParser["Gemini LLM Structured Parser"]
            MergeService["Resume Merge & Reconciliation"]
        end

        subgraph Intelligence["Matching & Embeddings Engine"]
            Embedder["SentenceTransformers (all-MiniLM-L6-v2)"]
            MatchingService["Hybrid Weighted Match Calculator"]
            Persistence["Batch Match Persistence"]
        end
    end

    subgraph Storage["Database & Cache"]
        Postgres[(PostgreSQL 16 Database)]
        MatchCache[(Candidate-Job Matches)]
    end

    UI --> CandidatesRouter
    Upload --> CandidatesRouter
    MatchView --> JobsRouter

    CandidatesRouter --> Pipeline
    Pipeline --> Embedder
    Embedder --> Postgres
    
    JobsRouter --> MatchingService
    MatchingService --> Embedder
    MatchingService --> Persistence
    Persistence --> MatchCache
    Postgres --> Persistence
```

---

## Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+)
- **Database & ORM**: [PostgreSQL 16](https://www.postgresql.org/), [SQLAlchemy 2.0](https://www.sqlalchemy.org/), [Alembic](https://alembic.sqlalchemy.org/)
- **Validation & Settings**: [Pydantic v2](https://docs.pydantic.dev/), [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- **AI & NLP**: [Google GenAI SDK](https://github.com/googleapis/python-genai), [Sentence-Transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`), [NumPy](https://numpy.org/)
- **Document Processing**: [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/), [pypdf](https://pypdf.readthedocs.io/)
- **Testing**: [pytest](https://docs.pytest.org/), [HTTPX](https://www.python-httpx.org/)

### Frontend
- **Framework**: [React 19](https://react.dev/), [Vite](https://vitejs.dev/)
- **Language**: [TypeScript](https://www.typescriptlang.org/)
- **Styling**: [Tailwind CSS v4](https://tailwindcss.com/)
- **Icons & Routing**: [Lucide React](https://lucide.dev/), [React Router v7](https://reactrouter.com/)
- **Charts & HTTP**: [Recharts](https://recharts.org/), [Axios](https://axios-http.com/)

### DevOps & Infrastructure
- **Containerization**: [Docker](https://www.docker.com/), [Docker Compose](https://docs.docker.com/compose/)

---

## Project Structure

```
talentiq-ai/
├── backend/
│   ├── alembic/                 # Database migration scripts & configuration
│   ├── app/
│   │   ├── api/                 # FastAPI API route controllers (candidates, jobs)
│   │   ├── core/                # Application configuration & environment settings
│   │   ├── database/            # SQLAlchemy session and Base setup
│   │   ├── models/              # SQLAlchemy database models (Candidate, Job, Match)
│   │   ├── schemas/             # Pydantic validation & response schemas
│   │   └── services/            # Core business logic:
│   │       ├── candidate_processor.py      # Schema translation & mapping
│   │       ├── candidate_search_service.py # SQL filtered search
│   │       ├── candidate_service.py        # Candidate CRUD & invalidation
│   │       ├── embedding_service.py        # Local vector embedding generation
│   │       ├── job_service.py              # Job CRUD & profile building
│   │       ├── llm_resume_parser.py        # Gemini structured LLM parser
│   │       ├── match_invalidation_service.py # Cache invalidation logic
│   │       ├── match_persistence_service.py  # Batch match persistence
│   │       ├── matching_service.py         # 3-pillar hybrid matching engine
│   │       ├── profile_text_service.py     # Profile text serialization
│   │       ├── resume_merge_service.py     # Deterministic & LLM result merger
│   │       ├── resume_parser.py            # PDF extraction & glyph normalization
│   │       ├── resume_pipeline_service.py  # Unified parsing pipeline
│   │       └── semantic_matching_service.py # Vector dot-product scoring
│   ├── scripts/                 # Unit & integration test suites, backfill utilities
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable UI components (Sidebar, AddCandidateForm)
│   │   ├── pages/               # Application pages (Dashboard, Candidates, Jobs)
│   │   ├── services/            # Axios API clients
│   │   ├── types/               # TypeScript interfaces
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml           # Multi-service orchestration (Postgres, Backend, Frontend)
└── README.md
```

---

## Getting Started

### Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 20 or higher (and `npm`)
- **PostgreSQL**: 16 (or Docker)
- **Google Gemini API Key**: [Google AI Studio](https://aistudio.google.com/)

---

### Option 1: Running with Docker Compose (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/KumarDhananjaya/talentiq-ai.git
   cd talentiq-ai
   ```

2. **Configure Environment Variables**:
   Create a `.env` file in the `backend/` directory:
   ```env
   DATABASE_URL=postgresql+psycopg://talentiq:talentiq_password@postgres:5432/talentiq_db
   GEMINI_API_KEY=your_gemini_api_key_here
   CORS_ORIGINS=http://localhost:5173
   ```

3. **Start the application**:
   ```bash
   docker compose up --build
   ```

4. **Access the services**:
   - **Frontend Web UI**: `http://localhost:5173`
   - **Backend API Docs (Swagger UI)**: `http://localhost:8000/docs`
   - **PostgreSQL Database**: `localhost:5433`

---

### Option 2: Local Development Setup

#### Backend Setup

1. **Navigate to the backend directory and create a virtual environment**:
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Configure the `.env` file** (`backend/.env`):
   ```env
   DATABASE_URL=postgresql+psycopg://talentiq:talentiq_password@localhost:5433/talentiq_db
   GEMINI_API_KEY=your_gemini_api_key_here
   CORS_ORIGINS=http://localhost:5173
   ```

4. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

5. **Start the FastAPI development server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure frontend environment** (`frontend/.env`):
   ```env
   VITE_API_URL=http://localhost:8000
   ```

4. **Start the Vite dev server**:
   ```bash
   npm run dev
   ```

---

## API Reference

Interactive API documentation and schema specifications are available at `http://localhost:8000/docs`.

### Candidates API (`/candidates`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/candidates/` | Create a new candidate profile. |
| `GET` | `/candidates/` | List all candidates in the talent pool. |
| `GET` | `/candidates/search` | Search candidates by skills and minimum experience. |
| `GET` | `/candidates/{id}` | Retrieve details for a specific candidate. |
| `PUT` | `/candidates/{id}` | Update candidate details and regenerate embeddings. |
| `DELETE` | `/candidates/{id}` | Delete candidate and invalidate associated matches. |
| `POST` | `/candidates/{id}/resume` | Upload a PDF resume, run AI parsing, and update profile. |

### Jobs & Matching API (`/jobs`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/jobs/` | Create a job posting with requirements and embeddings. |
| `GET` | `/jobs/` | List all job postings. |
| `GET` | `/jobs/{id}` | Retrieve details for a specific job posting. |
| `PUT` | `/jobs/{id}` | Update job description and invalidate cached matches. |
| `DELETE` | `/jobs/{id}` | Delete job posting and invalidate associated matches. |
| `GET` | `/jobs/{id}/matches` | Retrieve ranked candidate matches with score breakdowns. |
| `POST` | `/jobs/{id}/matches/recalculate` | Force recalculation and persistence of all candidate matches. |

---

## Running Tests

Backend unit and integration test suites are located in `backend/scripts/`:

```bash
cd backend
pytest scripts/ -v
```

Test coverage includes:
- Resume parsing & font subset glyph normalization
- Gemini LLM extraction & fallback merging
- Embedding generation & semantic scoring
- Hybrid match calculation & ranking
- Match invalidation lifecycle on profile updates
- API endpoints & database transaction rollbacks

---

## License

This project is open source and available under the [MIT License](LICENSE).
