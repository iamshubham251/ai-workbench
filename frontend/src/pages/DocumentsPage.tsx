import React, { useCallback, useEffect, useState } from 'react';
import {
  FileText,
  RefreshCw,
  Loader2,
  Inbox,
  AlertCircle,
} from 'lucide-react';
import { getDocuments, type DocumentRecord } from '../services/documentService';

function formatBytes(bytes: number): string {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
}

type LoadState = 'loading' | 'success' | 'error';

export const DocumentsPage: React.FC = () => {
  const [docs, setDocs] = useState<DocumentRecord[]>([]);
  const [loadState, setLoadState] = useState<LoadState>('loading');
  const [errorMsg, setErrorMsg] = useState('');

  const fetchDocs = useCallback(async () => {
    setLoadState('loading');
    try {
      const data = await getDocuments();
      setDocs(data);
      setLoadState('success');
    } catch (e) {
      setErrorMsg(e instanceof Error ? e.message : 'Failed to load documents');
      setLoadState('error');
    }
  }, []);

  useEffect(() => { fetchDocs(); }, [fetchDocs]);

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '4px' }}>Documents</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            All ingested documents available in the workbench.
          </p>
        </div>
        <button
          className="btn btn-outline"
          onClick={fetchDocs}
          disabled={loadState === 'loading'}
          aria-label="Refresh document list"
        >
          <RefreshCw size={14} className={loadState === 'loading' ? 'spin' : ''} />
          Refresh
        </button>
      </div>

      {loadState === 'loading' && (
        <div className="placeholder-page" style={{ height: '300px' }}>
          <Loader2 size={32} className="spin" style={{ color: 'var(--accent-color)' }} />
          <p style={{ marginTop: '16px', color: 'var(--text-muted)' }}>Loading documents…</p>
        </div>
      )}

      {loadState === 'error' && (
        <div className="placeholder-page" style={{ height: '300px' }}>
          <AlertCircle size={32} style={{ color: '#ef4444' }} />
          <p style={{ marginTop: '12px', color: '#ef4444' }}>{errorMsg}</p>
          <button className="btn btn-outline" style={{ marginTop: '16px' }} onClick={fetchDocs}>
            <RefreshCw size={14} /> Retry
          </button>
        </div>
      )}

      {loadState === 'success' && docs.length === 0 && (
        <div className="placeholder-page" style={{ height: '300px' }}>
          <Inbox size={48} style={{ color: 'var(--border-light)', marginBottom: '16px' }} />
          <h2>No documents yet</h2>
          <p>Upload a document from the dashboard to see it here.</p>
        </div>
      )}

      {loadState === 'success' && docs.length > 0 && (
        <div className="doc-library-table">
          <div className="doc-library-header">
            <span>Name</span>
            <span>Type</span>
            <span>Size</span>
            <span>Uploaded</span>
            <span>Status</span>
          </div>
          {docs.map((doc) => (
            <div key={doc.id} className="doc-library-row">
              <span className="doc-library-name">
                <FileText size={16} style={{ color: 'var(--accent-color)', flexShrink: 0 }} />
                <span>{doc.original_filename}</span>
              </span>
              <span className="doc-library-cell">{doc.extension.toUpperCase().replace('.', '')}</span>
              <span className="doc-library-cell">{formatBytes(doc.size_bytes)}</span>
              <span className="doc-library-cell">{formatDate(doc.created_at)}</span>
              <span className="doc-library-cell">
                <span className="badge badge-success">{doc.status}</span>
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
