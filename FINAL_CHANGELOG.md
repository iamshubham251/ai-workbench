# AI Workbench — Final Changelog & Release Notes

## 1. Project Overview

AI Workbench is an intelligent enterprise platform designed to automate document processing and inspection decision workflows. 
The system solves the problem of manual, time-consuming technical document reviews by ingesting unstructured data (PDFs, docs), extracting content via OCR and specialized parsing, and evaluating that data against known Standard Operating Procedures (SOPs) using Retrieval-Augmented Generation (RAG).

**Primary Workflow:**
1. A user uploads an inspection report (PDF).
2. The platform extracts the textual data (using PyMuPDF or Tesseract OCR).
3. Findings are structurally parsed.
4. The system queries an embedded vector knowledge base of SOPs.
5. Gemini (LLM) analyzes the findings against the retrieved SOP evidence.
6. A decision (APPROVE, REVIEW, REJECT) is generated alongside an evidence chain.
7. A final professional `.docx` Approval Note is generated for authenticated download and human-in-the-loop sign-off.

---

## 2. Final Architecture

**Data Flow:**
Frontend (React/Vite)
→ FastAPI (Python)
→ Authentication (JWT)
→ PostgreSQL (Metadata Storage)
→ Document Storage (Docker Volume)
→ PDF Processing Pipeline
→ PyMuPDF & Tesseract OCR
→ SOP / RAG Retrieval
→ Gemini AI (Analysis)
→ Decision Engine
→ DOCX Generation (python-docx)
→ Authenticated Download

**Docker Services:**
- `frontend`: Vite-based React application
- `backend`: FastAPI application on python:3.11-slim
- `db`: PostgreSQL 15 (primary database)
- `redis`: Redis server for task queues / caching

---

## 3. Major Features Added

### UI / UX
- **UI Polish**: Unified spacing, typography, and visual consistency across the enterprise dashboard.
- **Improved Workflow States**: Clear 5/5 timeline indicating real-time execution steps.
- **Improved Download Experience**: Secure `fetchWithAuth` object-URL mapping for protected files.
- **Demo Scenarios**: Real interactive scenarios executable directly from the dashboard.
- **System Architecture Page**: Interactive visualization of the system infrastructure and data flow.
- **Evidence Chain**: Dedicated layout component displaying finding summaries and severity labels.

### AI / Explainability
- **Inspection Findings**: Extracted structural findings.
- **Severity Labels**: Classified findings directly tied to visual indicators.
- **SOP Evidence**: Embedded contextual reference snippets.
- **Evidence Chain**: Clear traceability from document → finding → SOP → AI rationale.
- **Decision Explanation**: The explicit reasoning path Gemini used to reach the decision.
- **APPROVE / REVIEW / REJECT**: Discrete actionable workflow outputs.

### Workflow
- **Document Extraction**: Multimodal pipeline for PDF scanning and image parsing.
- **SOP Retrieval**: Vector-based semantic search across established enterprise guidelines.
- **AI Analysis**: Multi-agent reasoning prompt execution.
- **Decision**: Deterministic formatting of LLM intelligence.
- **Document Generation**: Formatted binary output creation.

### Human-in-the-loop
- **Human Review Sign-off**: Manual override checkpoint capability.
- **Review Workflow**: Middle-state triggering operator intervention.
- **Generated Sign-off Section**: A physical checklist appended to the final DOCX artifact.

### Document Generation
- **Professional DOCX**: Standardized formatting and enterprise layout.
- **Inspection Findings Table**: Tabular layout of all detected issues mapped to severities.
- **Timestamp**: ISO formatting injected into the output document metadata.
- **Human Review Checklist**: Explicit approval blocks for downstream auditors.

### Reliability
- **Gemini Retry Logic**: Graceful degradation and retry mechanisms.
- **Transient 503/429 Handling**: Exponential backoff implementations for Google AI Studio instability.
- **Structured Backend Errors**: Dedicated exception mappings for internal crashes.
- **Frontend-Readable Errors**: User-facing toast notifications detailing error specifics.
- **CORS-Safe Error Responses**: Preflight validation ensuring error payloads do not violate CORS.

### Security
- **JWT Authentication**: OAuth2 Password Bearer implementation.
- **Authenticated DOCX Downloads**: Secured route endpoints mapping user sessions to file streams.
- **No Public Unauthenticated File Access**: All `/api/documents/` and physical paths protected by dependencies.

---

## 4. Important Bug Fixes

### Docker Build Context
- **Problem**: The backend virtual environment was included in the Docker build context, bloating the build by over 1.17GB and drastically increasing deploy times.
- **Fix**: Added a `.dockerignore` for the backend.

### PostgreSQL BOOLEAN
- **Problem**: PostgreSQL rejected `DEFAULT 1` for BOOLEAN column `is_active` when creating the `users` table via the setup scripts.
- **Fix**: Safely transitioned constraints to `DEFAULT TRUE` and dropped the `DEFAULT` constraint inside the Python repository layer to maintain SQLite test compatibility.

### CORS / Backend Errors
- **Problem**: Unhandled backend errors resulted in opaque frontend "Failed to fetch" due to missed CORS headers on 500 responses.
- **Fix**: Implemented structured exception handlers and global middleware CORS handling.

### Gemini 503
- **Problem**: Temporary provider failures (503 Service Unavailable) crashed workflows.
- **Fix**: Introduced a retry mechanism with exponential backoff on AI calls.

### PDF Storage
- **Problem**: The Docker upload path differed from the mounted volume, causing physical file isolation and 404s during OCR.
- **Fix**: Adjusted configuration to use `UPLOAD_DIR=/app/data/uploads`.

### Ghost Test Document
- **Problem**: The automated test suite inserted `inspection.pdf` database records without creating physical PDF files on disk, causing processing crashes when running workflows on them.
- **Fix**: Identified as a test artifact; implemented Demo Scenarios providing actual valid PDF fixtures.

### DOCX Download
- **Problem**: Browser `<a href>` standard requests did not include the JWT Authorization header, causing 401s during download.
- **Fix**: Transitioned to an authenticated `fetchWithAuth()` using `Blob` and `URL.createObjectURL()`.

---

## 5. Demo Scenarios

### APPROVE
**Pipeline Alpha**
- **Inspection Conditions**: All pipeline pressures and temperatures nominal. No visible wear.
- **Relevant SOP**: General Operational Parameters SOP.
- **Expected Decision**: APPROVE
- **Generated Artifact**: Approval Note with standard signatures.

### REVIEW
**Generator Beta**
- **Inspection Conditions**: The voltage data was missing/unreadable due to smudged logs.
- **Relevant SOP**: Electrical Component Documentation Standard.
- **Expected Decision**: REVIEW
- **Generated Artifact**: Review Note requesting human intervention to locate and input the missing voltage metrics.

### REJECT
**Boiler Gamma**
- **Inspection Conditions**: Micro-fractures detected along the secondary pressure seal.
- **Relevant SOP**: Pressure Vessel Safety Integrity SOP (states any fracture requires immediate rejection and offline maintenance).
- **Expected Decision**: REJECT
- **Generated Artifact**: Rejection Note with safety escalation warnings.

*(These are synthetic demo fixtures intended for presentation purposes).*

---

## 6. Demo Fixtures

The synthetic demo files are stored locally in the project repository to guarantee an identical test state for reviewers:

**Inspection Reports:**
- `demo_fixtures/pdfs/demo_inspection_approve.pdf`
- `demo_fixtures/pdfs/demo_inspection_review.pdf`
- `demo_fixtures/pdfs/demo_inspection_reject.pdf`

**Reference SOPs:**
- `demo_fixtures/pdfs/demo_sop_approve.pdf`
- `demo_fixtures/pdfs/demo_sop_review.pdf`
- `demo_fixtures/pdfs/demo_sop_reject.pdf`

---

## 7. Generated DOCX

The final generated DOCX artifact encapsulates the entire workflow logic. It includes:
- **Title and Timestamp**
- **Inspection Findings Table**: Lists the issue description alongside its interpreted severity.
- **Decision**: Clear display of the AI's ruling.
- **SOP Evidence & Reasoning**: Direct quotations from the knowledge base supporting the ruling.
- **Human Review Section**: A trailing block intended for a physical signature and date.
- **Authenticated Download**: Delivered securely via backend API streams.

---

## 8. Error Handling

- **400**: Used for invalid states or malformed entity requests.
- **401**: Global router enforcement for missing or invalid JWT tokens.
- **422**: FastAPI automatic validation failures (Pydantic schema violations).
- **500**: Caught by global exception handlers to ensure CORS headers are appended, preventing opaque frontend failures.
- **503**: Temporary Gemini provider failures are retried automatically. If exhausted, they return as structured 503 service-unavailable errors rather than crashing the thread.

---

## 9. Testing

The platform enforces a robust testing suite leveraging `pytest`.
- **Global Auth Mocks**: A dynamic override system allows the testing client to bypass JWT validation across the entire FastAPI app seamlessly.
- **Isolated SQLite DBs**: A dynamic `autouse` fixture isolates the SQLAlchemy engine to a temporary on-disk SQLite database, completely eliminating data leakage across stateful tests.

### Major Test Categories
- **Auth**: Access control and route protection.
- **Documents**: Upload validation, size limits, and persistence.
- **SOP/RAG**: Vector querying and context relevancy matching.
- **Gemini**: Retry mechanisms and structural validation of LLM outputs.
- **Workflow**: End-to-end integration matching inputs to expected decisions.

*Manual verification has fully succeeded across all live Docker containers.*

---

## 10. Docker Deployment

The application is deployed across four distinct Docker containers:
1. `ai-workbench-frontend`: Serves the Vite React application.
2. `ai-workbench-backend`: Exposes the FastAPI endpoints. Connects internally to Redis and Postgres.
3. `ai-workbench-db`: PostgreSQL relational database hosting user and document metadata.
4. `ai-workbench-redis`: Memory store for future asynchronous scaling.

- **Persistent Data Storage**: Docker volumes are mounted to `/app/data/uploads` ensuring physical files persist across container restarts.
- **Configuration**: Uses `.env` files for seamless environment parity.

---

## 11. Security

- **JWT Authentication**: Enforced globally on API routers.
- **Authenticated Downloads**: Blob mapping securely fetches files.
- **Server-side API keys**: Gemini API keys are never exposed to the frontend browser context.
- **Docker Variables**: Secrets are injected securely via `.env`.

---

## 12. Known Limitations

- **OCR Dependency**: Tesseract requires clean imagery. Heavy artifacting can result in dropped extraction accuracy.
- **In-Memory Embeddings**: The vector search currently uses a naive in-memory distance calculation instead of a dedicated vector database (like pgvector or Pinecone) which may struggle to scale beyond a few thousand SOP pages.

---

## 13. Final Verification

- [x] Login
- [x] Logout
- [x] Upload
- [x] PDF extraction
- [x] OCR
- [x] SOP retrieval
- [x] Gemini
- [x] APPROVE
- [x] REVIEW
- [x] REJECT
- [x] DOCX generation
- [x] DOCX download
- [x] Error handling
- [x] Docker
- [x] PostgreSQL
- [x] Redis
- [x] Automated tests

---

## Final Test Infrastructure Repair
- **Authentication Fixture Issue**: FastAPI's router-level dependency injection (`Depends(get_current_user)`) bypassed `dependency_overrides`. Fixed by configuring the `TestClient` to natively pass a valid JWT mapped to an injected SQLite test user.
- **Database Isolation Issue**: SQLite test databases inherited the host's `DATABASE_URL`, causing state to leak into the production PostgreSQL container. Fixed by correctly scoping mock parameters and strictly injecting a clean SQLAlchemy session per test.
- **Final Test Count**: 268 passed, 0 failed, 0 skipped.
- **Production Database**: Fully protected; unmodified during testing.
