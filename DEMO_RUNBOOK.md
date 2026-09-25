# AI Workbench — Live Demo Runbook

## A. 30-Second Elevator Pitch
"AI Workbench is an intelligent document-processing platform that automates manual technical reviews. Instead of engineers reading 50-page inspection reports and manually cross-referencing company SOPs, AI Workbench extracts the text, semantically searches the organization's SOPs, uses AI to evaluate the findings against those rules, and produces a deterministic approval decision and a formatted DOCX deliverable for human sign-off."

## B. 2-Minute Product Explanation
"Let me show you how it works under the hood. When we upload a document, AI Workbench doesn't just pass it to ChatGPT. That’s dangerous and leads to hallucinations.
Instead, it orchestrates a pipeline:
1. **Extraction**: It uses `PyMuPDF` and `Tesseract OCR` to extract raw text, even from scanned legacy PDFs.
2. **Knowledge Grounding**: It chunks and embeds the text, and performs local RAG (Retrieval-Augmented Generation) against a local vector database of company SOPs.
3. **Grounded AI**: The retrieved SOP rules and the inspection findings are fed to Gemini, explicitly constrained to ONLY use the retrieved evidence.
4. **Deterministic Decision**: The AI classifies the findings by severity. A hard-coded rules engine (not the AI) makes the final APPROVE, REVIEW, or REJECT call based on that severity.
5. **Deliverable**: A Python microservice generates a formatted `.docx` file ready for final human sign-off."

## C. 5-Minute Live Demo Flow
1. **Login & Dashboard**: Show the React frontend and real-time operational stats.
2. **Upload Scenarios**: Use the interactive "Demo Scenarios" panel to quickly trigger 3 specific edge-cases.
3. **Workflow Execution**: Run the "Alpha (Approve)", "Beta (Review)", and "Gamma (Reject)" scenarios.
4. **Live Execution Timeline**: Explain what the backend is doing in real-time as the 5/5 status tracker updates.
5. **Evidence Chain**: Show how the AI's findings map directly to SOP evidence snippets and severity labels.
6. **Download Artifact**: Download the generated DOCX and open it to show the tabular layout and Human Sign-off block.

## D. Exact Steps to Perform in the Browser
1. Open `http://localhost:5173`.
2. Login with `admin@ai-workbench.local` / `admin`.
3. Scroll to the **Demo Scenarios** panel on the Dashboard.
4. Click **Run Alpha (APPROVE)**.
5. Let the workflow timeline run. Talk through the stages.
6. When complete, scroll down to the **Evidence Chain**.
7. Click the **Download Note** button.
8. Open the downloaded DOCX file in Microsoft Word or a viewer.

## E. What to say while each workflow stage runs
- **Document Extraction**: "Right now, the backend is running PyMuPDF and Tesseract OCR to parse the PDF."
- **SOP Retrieval**: "Now it's using sentence-transformers to query our local database for the specific SOPs relevant to this equipment."
- **AI Analysis**: "Gemini is now cross-referencing the inspection findings against the SOP rules we just retrieved."
- **Decision**: "A deterministic Python rules-engine just evaluated the severity of the findings. The AI does not make the final call; the rules engine does."
- **Document Generation**: "It just generated a binary DOCX file using python-docx."

## F. How to demonstrate the 3 Decisions
- **APPROVE (Pipeline Alpha)**: Explain that all parameters (pressure, temp) were nominal according to the SOP.
- **REVIEW (Generator Beta)**: Explain that the voltage was not tested (missing data). The rules engine is programmed to require human intervention (REVIEW) when data is incomplete.
- **REJECT (Boiler Gamma)**: Explain that a fracture was found. The SOP explicitly states fractures require immediate shutdown, triggering a critical REJECT.

## G. How to explain the Evidence Chain
Point to the screen: "This is our transparency layer. We don't just output a decision. We show you the exact finding extracted from the document, its severity label, and the specific snippet from the SOP that justifies that severity. If the AI gets it wrong, you can see exactly why."

## H. How to show the generated DOCX
Open the downloaded `.docx` file. Point out:
1. The structured **Inspection Findings Table** mapping issues to severity.
2. The **Supporting SOP Evidence** section listing direct quotations.
3. The **Human Review (Sign-off)** block at the bottom, proving that AI Workbench accelerates humans, but doesn't replace final accountability.

## I. Backup procedure if Gemini temporarily fails
If Gemini returns a 503 or 429, wait a few seconds and run the scenario again. The backend has exponential backoff, but if it ultimately fails, explain: "We're hitting a rate limit on the Google AI Studio free tier. In production, this would be routed to a dedicated Vertex AI endpoint or a local, offline model using our `ModelRouter` abstraction."

## J. Backup procedure if Docker/services are not running
Run `docker compose -f docker-compose.prod.yml up -d` in the terminal. Wait 15 seconds. Refresh the browser.

## K. Things NOT to click/change during the demo
- Do NOT upload massive non-PDF files.
- Do NOT click around randomly while a workflow is actively processing.
- Do NOT try to modify the codebase or `.env` files live.

## L. Demo recovery checklist
If something breaks completely:
1. "Let me just refresh the environment."
2. `docker compose -f docker-compose.prod.yml restart backend`
3. Reload the frontend.
4. Continue smoothly.
