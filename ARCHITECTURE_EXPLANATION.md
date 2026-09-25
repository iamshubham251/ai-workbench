# AI Workbench — Technical Architecture

## 1. High-Level Architecture
AI Workbench operates on a microservice-inspired monolithic architecture. The frontend is a React SPA (Single Page Application) that communicates with a FastAPI Python backend over a REST API. The backend orchestrates data across PostgreSQL (metadata), persistent Docker volumes (file storage), a local RAG vector store (SQLite), and external APIs (Gemini).

## 2. Frontend → Backend Flow
1. User interacts with the React UI (Vite, TypeScript).
2. The UI makes an HTTP request via `fetch` (with a JWT Bearer token).
3. FastAPI receives the request, validates the JWT, and routes it to a service layer.
4. The service layer executes business logic, interacts with repositories, and returns Pydantic-validated JSON.

## 3. Authentication Flow
- **Login:** The user submits credentials to `/api/auth/token`. The backend verifies the password hash via passlib/bcrypt against PostgreSQL.
- **Token:** The backend mints a JWT (JSON Web Token) containing the user's `sub` (email) and an expiration time, signed with a secret key.
- **Authorization:** Protected endpoints use `Depends(get_current_user)`, which decodes the JWT and fetches the user from the database before granting access.

## 4. Document Upload Flow
1. File is POSTed as `multipart/form-data` to `/api/documents/upload`.
2. Backend validates size and MIME type.
3. A unique UUID is generated. The physical file is saved to `/app/data/uploads/<uuid>/<filename>`.
4. A metadata record is created in PostgreSQL linking the UUID to the user.

## 5. PDF Extraction/OCR Flow
When a workflow is triggered:
1. `pdf_content_detector.py` checks if the PDF has embedded text.
2. If embedded text exists, `pypdf` extracts it.
3. If pages are scanned images, `PyMuPDF` rasterizes the pages into images, and `Tesseract OCR` runs optical character recognition to extract the text.
4. `document_normalizer.py` combines all text into a structured, page-aware object.

## 6. SOP Retrieval (RAG) Flow
1. The extracted inspection text is sent to the `rag_service.py`.
2. The text is embedded using a local `sentence-transformers` model.
3. The embedding is compared against all SOP chunks in the local SQLite knowledge base using Cosine Similarity.
4. Chunks exceeding a strict relevance threshold are retrieved as "Evidence".

## 7. Gemini Reasoning Flow
1. `AgentManager` takes the inspection text and the retrieved SOP Evidence.
2. It constructs a "Grounded Prompt" that explicitly separates the task from the evidence, instructing the AI *not* to invent facts.
3. `ModelRouter` delegates the prompt to the `GeminiModelProvider`.
4. Gemini analyzes the data and returns a structured JSON response containing specific "findings" and their "severity" (High, Medium, Low).

## 8. Decision Flow
This is deliberately deterministic, **not** AI-driven:
1. `ApprovalDecisionService` receives the AI's severity-tagged findings.
2. Rule: If ANY finding is High severity → **REJECT**.
3. Rule: If ANY finding is Medium severity, or NO findings are extracted → **REVIEW**.
4. Rule: If ALL findings are Low severity, or explicitly nominal → **APPROVE**.

## 9. DOCX Generation Flow
1. `approval_note_generator.py` uses `python-docx` to create a binary Word document.
2. It injects the workflow metadata, the decision, a table of the AI's findings, and the supporting SOP evidence.
3. It appends a physical signature block for human sign-off.
4. The file is saved to `/app/data/outputs/` and the path is saved to the database.

## 10. Storage Architecture
- **PostgreSQL:** Stores relational data (Users, Document Metadata, Workflow History).
- **SQLite:** Stores local RAG data (Document Chunks, Vector Embeddings). Kept local for fast in-memory similarity math.
- **Docker Volumes:** Mounts host directories to `/app/data/uploads` and `/app/data/outputs` to ensure physical PDFs and DOCXs persist if the container crashes.

## 11. Database Role (PostgreSQL)
PostgreSQL is the source of truth for the application state. It manages user accounts, tracks who uploaded which documents, and records the history and outcomes of all executed workflows.

## 12. Redis Role
Redis is deployed in the Docker topology to support horizontal scaling. While current workflows are synchronous, Redis is positioned to act as the message broker for Celery, allowing long-running tasks (like bulk OCR or embedding 1,000-page SOPs) to be pushed to background workers.

## 13. Docker Architecture
The system relies on Docker Compose for deterministic environments:
- `frontend`: Built with Node, served natively.
- `backend`: Built on `python:3.11-slim`, runs Uvicorn.
- `db`: Official `postgres:15-alpine` image.
- `redis`: Official `redis:7-alpine` image.
Containers communicate over an internal Docker network, exposing only ports 5173 (UI) and 8000 (API) to the host.

## 14. Error Handling
- **Backend:** Global exception handlers in FastAPI catch domain exceptions (e.g., `PdfProcessingError`, `ModelProviderError`) and convert them into standardized JSON responses with appropriate HTTP codes (400, 422, 503).
- **Gemini Retries:** The `GeminiModelProvider` uses `tenacity` to apply exponential backoff if Google's API returns transient 429 (Rate Limit) or 503 (Unavailable) errors.
- **Frontend:** API clients catch these standardized errors and dispatch user-friendly Toast notifications.

## 15. Security Considerations
- JWT tokens are short-lived.
- Passwords are salted and hashed via bcrypt.
- Files are stored outside the web root.
- File downloads require authenticated `fetch` requests with bearer tokens.
- SQL Injection is mitigated by SQLAlchemy ORM parameterized queries.

## 16. Current Limitations
- **Vector Search:** The current `vector_similarity.py` calculates dot products in Python memory. This is O(N) and will bottleneck beyond ~10,000 chunks.
- **Synchronous Execution:** The API blocks the HTTP response while waiting for OCR and Gemini, which could cause browser timeouts on massive PDFs.

## 17. Production Scaling Roadmap
1. **Async Workers:** Migrate the `execute_from_document()` method to push a task to Redis and return a `task_id` immediately to the frontend.
2. **Dedicated Vector DB:** Migrate SQLite embeddings to `pgvector` inside the existing PostgreSQL container to leverage HNSW indexing for O(log N) search times.
3. **Cloud Storage:** Swap the local `LocalStorage` class for an `S3Storage` class implementing the same interface.
