# AI Workbench — Judge Q&A

## Business Value & Core Problem

**Q: What problem does AI Workbench solve?**
A: It eliminates the manual bottleneck of reviewing technical documents against organizational policies. Engineers waste hours reading inspection reports, cross-referencing SOPs, and writing approval notes. We automate the extraction, cross-referencing, and document generation so humans only have to review the final output.

**Q: Why is AI needed here?**
A: Technical reports contain unstructured natural language, nuance, and domain-specific terminology that rigid rules cannot parse. AI is required to semantically understand the finding (e.g., "hairline fracture on valve") and map it to the corresponding SOP rule (e.g., "structural integrity failure").

**Q: Why not use a normal rule-based system?**
A: A normal rule-based system requires structured inputs (like a web form with dropdowns). Real-world enterprise data lives in unstructured PDFs. You can't write a regex to understand "the secondary seal appears slightly deformed."

**Q: What makes this different from simply uploading a PDF to ChatGPT/Gemini?**
A: Uploading a PDF to ChatGPT causes hallucinations, isn't constrained by your private company SOPs, lacks an auditable evidence chain, doesn't generate a standardized binary DOCX, and doesn't enforce deterministic approval rules. Our system forces the AI to only extract findings and relies on a deterministic Python rules-engine for the final approval decision.

**Q: What is the human-in-the-loop component?**
A: The system generates a formatted DOCX containing all findings and the AI's recommendation, but it includes a trailing physical sign-off block. A human reviewer remains accountable for the final approval. Also, ambiguous or incomplete data forces the system into a "REVIEW" state, mandating human intervention.

## AI & Architecture

**Q: Where exactly is AI used?**
A: AI is used in two specific places:
1. **Embeddings:** A local sentence-transformers model maps document chunks to vector embeddings.
2. **Analysis:** The Gemini LLM receives the inspection text and the retrieved SOP evidence, and is prompted strictly to extract findings and classify their severity based *only* on the evidence.

**Q: How does SOP retrieval work?**
A: It uses local RAG (Retrieval-Augmented Generation). Uploaded SOPs are normalized, chunked, and embedded into a local SQLite vector store using sentence-transformers. When an inspection report is processed, we calculate cosine similarity against the SOP chunks and retrieve only those above a strict relevance threshold.

**Q: How does the system prevent unsupported decisions?**
A: The AI is decoupled from the final decision. The LLM only classifies the severity of the findings (e.g., High, Medium, Low). A deterministic Python service then maps those severities to outcomes: any High severity finding equals REJECT, any missing data equals REVIEW. 

**Q: What happens when inspection data is incomplete?**
A: If the AI cannot find necessary data points required by the SOP, it flags it. Our deterministic rules engine interprets missing or medium-severity data as a trigger for a "REVIEW" decision, ensuring humans investigate missing parameters rather than falsely approving them.

**Q: Why does the system return REVIEW?**
A: REVIEW acts as a safety net. It is returned when there are no findings, incomplete data, or medium-severity warnings that require human domain expertise. The system refuses to auto-approve anything that isn't perfectly clean.

**Q: What happens when the AI provider is unavailable?**
A: The backend implements exponential backoff and retry logic. If the provider remains unavailable (e.g., a 503 from Google AI Studio), it fails gracefully with a structured error, showing a user-friendly toast notification in the frontend rather than crashing the pipeline.

## Technical Choices

**Q: Why PyMuPDF and Tesseract?**
A: `pypdf` is great for natively embedded text, but many enterprise documents are scanned images. `PyMuPDF` allows us to rasterize those scanned PDF pages into images, and `Tesseract` performs Optical Character Recognition (OCR) to extract the text reliably.

**Q: Why PostgreSQL?**
A: PostgreSQL provides robust, production-ready ACID compliance for our user metadata, authentication models, and document relationship mapping. 

**Q: Why Redis?**
A: Redis is included in the Docker topology to support asynchronous task queues (like Celery) for the future. Currently, workflows execute synchronously, but Redis paves the way for handling massive bulk uploads in the background.

**Q: Why FastAPI?**
A: FastAPI is python-native, incredibly fast (Starlette/Pydantic), and makes asynchronous IO (like network calls to Gemini) highly efficient. It also auto-generates our OpenAPI documentation.

**Q: Why React?**
A: React (via Vite) gives us a highly responsive, component-driven UI that handles complex state (like a live 5-step workflow timeline) smoothly and efficiently.

## Security & Scaling

**Q: How does authentication work?**
A: We use OAuth2 Password Bearer with JWTs (JSON Web Tokens). Endpoints are protected by a `Depends(get_current_user)` FastAPI dependency that validates the JWT signature against our secret key before allowing access.

**Q: How are uploaded documents stored?**
A: Metadata is stored in PostgreSQL. The physical binary files are stored on disk in a persistent Docker volume (`/app/data/uploads`), ensuring they survive container restarts and remain isolated from the web root.

**Q: How are generated documents downloaded securely?**
A: Standard `<a>` href links can't pass JWT headers. We use a secure `fetchWithAuth()` function that retrieves the file as a Blob using the JWT, then generates a temporary `URL.createObjectURL()` in the browser for the user to download.

**Q: What happens if two users use the system simultaneously?**
A: The system is stateless on the backend (aside from the database/disk). FastAPI handles requests concurrently via ASGI. Each workflow execution is isolated by its `document_id` and unique `workflow_id`.

**Q: How would this scale?**
A: 
1. **Background Queues:** Move the synchronous workflow to a Celery/Redis background task.
2. **Vector DB:** Replace the SQLite in-memory cosine similarity with a dedicated vector database like Pinecone or pgvector.
3. **Stateless Storage:** Move local file storage to AWS S3 or Google Cloud Storage.

**Q: What are the current limitations?**
A: 
1. Similarity search uses a naive in-memory dot product which won't scale to millions of chunks.
2. OCR via Tesseract struggles with highly distorted or low-DPI scans.
3. Workflows block the HTTP request thread while waiting for the LLM.

**Q: How would you evaluate the AI decisions?**
A: We'd implement an evaluation pipeline using a golden dataset of past human-reviewed inspections. We would track precision/recall on the AI's severity classifications compared to historical human judgments.

**Q: How would you replace the current embedding/retrieval layer at scale?**
A: I would migrate the SQLite chunk storage to a `pgvector` extension inside our existing PostgreSQL database, allowing us to perform highly optimized ANN (Approximate Nearest Neighbor) searches at scale without adding a new infrastructure component.
