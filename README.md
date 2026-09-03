# AI Workbench

## Purpose
A modular, extensible AI Workbench project foundation designed to incrementally integrate document processing, OCR, local RAG, agent management, model routing, local tools, and document generation.

## Architecture
The project strictly separates the frontend and backend:
- **Frontend**: React + TypeScript + Vite
- **Backend**: Python + FastAPI
- **Data**: Dedicated directories for uploads, knowledge base, and generated outputs
- **AI/Agents/RAG/Tools**: Modular placeholder directories for future integrations

## Prerequisites
- Node.js (v18+)
- Python (3.9+)

## Frontend Setup/Run
1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## Backend Setup/Run
1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   # source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the backend server:
   ```bash
   uvicorn main:app --reload
   ```

## API Health Endpoint
- **URL**: `GET http://localhost:8000/api/health`
- **Response**: `{"status": "ok", "message": "Backend is running"}`
