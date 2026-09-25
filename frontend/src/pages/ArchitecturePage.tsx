import React from 'react';
import { Layers, Database, Lock, Cpu, Server, CheckCircle, FileOutput } from 'lucide-react';
import './DashboardPage.css'; // Reuse dashboard styles

export const ArchitecturePage: React.FC = () => {
  return (
    <div className="dashboard-layout" style={{ maxWidth: '900px', margin: '0 auto', paddingTop: '40px' }}>
      <div className="dashboard-main" style={{ gap: '32px' }}>
        <div>
          <h1 style={{ fontSize: '2rem', marginBottom: '8px' }}>System Architecture</h1>
          <p style={{ color: 'var(--text-secondary)' }}>AI Workbench End-to-End Compliance Pipeline</p>
        </div>

        <div className="card" style={{ padding: '32px' }}>
          <h3 style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Server size={20} className="text-accent" />
            Logical Data Flow
          </h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', position: 'relative' }}>
            {/* Draw a connecting line behind the nodes */}
            <div style={{ position: 'absolute', left: '24px', top: '24px', bottom: '24px', width: '2px', background: 'var(--border-color)', zIndex: 0 }} />
            
            <div className="evidence-item" style={{ position: 'relative', zIndex: 1 }}>
              <span className="severity-indicator severity-low"><Layers size={14} /></span>
              <p><strong>React Frontend (Vite)</strong><br/><span style={{ fontSize: '0.85em', color: 'var(--text-muted)' }}>Collects instructions and manages documents.</span></p>
            </div>
            
            <div className="evidence-item" style={{ position: 'relative', zIndex: 1 }}>
              <span className="severity-indicator severity-low"><Lock size={14} /></span>
              <p><strong>FastAPI Backend & JWT Auth</strong><br/><span style={{ fontSize: '0.85em', color: 'var(--text-muted)' }}>Secure entry point and API routing.</span></p>
            </div>
            
            <div className="evidence-item" style={{ position: 'relative', zIndex: 1 }}>
              <span className="severity-indicator severity-low"><Database size={14} /></span>
              <p><strong>PostgreSQL & Docker Volumes</strong><br/><span style={{ fontSize: '0.85em', color: 'var(--text-muted)' }}>Metadata persistence and physical file storage (/app/data/uploads).</span></p>
            </div>

            <div className="evidence-item" style={{ position: 'relative', zIndex: 1 }}>
              <span className="severity-indicator severity-medium"><Cpu size={14} /></span>
              <p><strong>PyMuPDF & Tesseract OCR</strong><br/><span style={{ fontSize: '0.85em', color: 'var(--text-muted)' }}>Extracts raw text from uploaded inspection PDFs.</span></p>
            </div>
            
            <div className="evidence-item" style={{ position: 'relative', zIndex: 1 }}>
              <span className="severity-indicator severity-medium"><Database size={14} /></span>
              <p><strong>SOP Retrieval (RAG)</strong><br/><span style={{ fontSize: '0.85em', color: 'var(--text-muted)' }}>Local sentence-transformers find exact SOP matches.</span></p>
            </div>

            <div className="evidence-item" style={{ position: 'relative', zIndex: 1 }}>
              <span className="severity-indicator severity-high"><Cpu size={14} /></span>
              <p><strong>Gemini AI (google-genai)</strong><br/><span style={{ fontSize: '0.85em', color: 'var(--text-muted)' }}>Analyzes extraction text against SOP logic to isolate findings.</span></p>
            </div>

            <div className="evidence-item" style={{ position: 'relative', zIndex: 1 }}>
              <span className="severity-indicator severity-low"><CheckCircle size={14} /></span>
              <p><strong>Decision Engine</strong><br/><span style={{ fontSize: '0.85em', color: 'var(--text-muted)' }}>Rules engine evaluates findings severity (APPROVE/REVIEW/REJECT).</span></p>
            </div>

            <div className="evidence-item" style={{ position: 'relative', zIndex: 1 }}>
              <span className="severity-indicator severity-low"><FileOutput size={14} /></span>
              <p><strong>DOCX Generation & Download</strong><br/><span style={{ fontSize: '0.85em', color: 'var(--text-muted)' }}>python-docx generates the final artifact; fetchWithAuth streams the Blob.</span></p>
            </div>
          </div>
        </div>

        <div className="card" style={{ padding: '32px' }}>
          <h3 style={{ marginBottom: '24px' }}>Docker Services</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            <div className="evidence-item"><p><strong>ai-workbench-frontend-1</strong><br/>Port 5173</p></div>
            <div className="evidence-item"><p><strong>ai-workbench-backend-1</strong><br/>Port 8000</p></div>
            <div className="evidence-item"><p><strong>ai-workbench-db-1</strong><br/>PostgreSQL 15</p></div>
            <div className="evidence-item"><p><strong>ai-workbench-redis-1</strong><br/>Redis 7</p></div>
          </div>
        </div>
      </div>
    </div>
  );
};
