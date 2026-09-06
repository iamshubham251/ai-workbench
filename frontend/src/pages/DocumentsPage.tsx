import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  FileText,
  RefreshCw,
  Loader2,
  Inbox,
  AlertCircle,
  Search,
  Upload,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { getDocuments, type DocumentRecord } from '../services/documentService';

function formatBytes(bytes: number): string {
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }

  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(iso: string): string {
  const date = new Date(iso);

  return date.toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  });
}

function getDocumentType(extension: string): string {
  return extension.toUpperCase().replace('.', '');
}

type LoadState = 'loading' | 'success' | 'error';

export const DocumentsPage: React.FC = () => {
  const navigate = useNavigate();

  const [docs, setDocs] = useState<DocumentRecord[]>([]);
  const [loadState, setLoadState] = useState<LoadState>('loading');
  const [errorMsg, setErrorMsg] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const fetchDocs = useCallback(async () => {
    setLoadState('loading');
    setErrorMsg('');

    try {
      const data = await getDocuments();
      setDocs(data);
      setLoadState('success');
    } catch (error) {
      setErrorMsg(
        error instanceof Error
          ? error.message
          : 'Failed to load documents',
      );
      setLoadState('error');
    }
  }, []);

  useEffect(() => {
    void fetchDocs();
  }, [fetchDocs]);

  const filteredDocs = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();

    if (!query) {
      return docs;
    }

    return docs.filter((doc) =>
      doc.original_filename.toLowerCase().includes(query),
    );
  }, [docs, searchQuery]);

  return (
    <div className="documents-page">
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          gap: '20px',
          marginBottom: '24px',
          flexWrap: 'wrap',
        }}
      >
        <div>
          <h1
            style={{
              fontSize: '1.5rem',
              fontWeight: 600,
              marginBottom: '6px',
            }}
          >
            Documents
          </h1>

          <p
            style={{
              color: 'var(--text-secondary)',
              fontSize: '0.9rem',
            }}
          >
            Manage documents uploaded to your AI Workbench.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            className="btn btn-outline"
            onClick={() => void fetchDocs()}
            disabled={loadState === 'loading'}
            aria-label="Refresh document list"
          >
            <RefreshCw
              size={14}
              className={loadState === 'loading' ? 'spin' : ''}
            />
            Refresh
          </button>

          <button
            className="btn btn-primary"
            onClick={() => navigate('/')}
          >
            <Upload size={14} />
            Upload document
          </button>
        </div>
      </div>

      {loadState === 'success' && docs.length > 0 && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '16px',
            marginBottom: '18px',
            flexWrap: 'wrap',
          }}
        >
          <div
            style={{
              color: 'var(--text-secondary)',
              fontSize: '0.85rem',
            }}
          >
            {docs.length} {docs.length === 1 ? 'document' : 'documents'}
          </div>

          <div
            style={{
              position: 'relative',
              width: 'min(320px, 100%)',
            }}
          >
            <Search
              size={15}
              style={{
                position: 'absolute',
                left: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: 'var(--text-muted)',
                pointerEvents: 'none',
              }}
            />

            <input
              type="search"
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder="Search documents..."
              aria-label="Search documents"
              style={{
                width: '100%',
                padding: '9px 12px 9px 36px',
                borderRadius: '8px',
                border: '1px solid var(--border-color)',
                background: 'var(--surface-color)',
                color: 'var(--text-primary)',
                outline: 'none',
              }}
            />
          </div>
        </div>
      )}

      {loadState === 'loading' && (
        <div className="placeholder-page" style={{ height: '300px' }}>
          <Loader2
            size={32}
            className="spin"
            style={{ color: 'var(--accent-color)' }}
          />
          <p
            style={{
              marginTop: '16px',
              color: 'var(--text-muted)',
            }}
          >
            Loading documents...
          </p>
        </div>
      )}

      {loadState === 'error' && (
        <div className="placeholder-page" style={{ height: '300px' }}>
          <AlertCircle size={32} style={{ color: '#ef4444' }} />

          <p
            style={{
              marginTop: '12px',
              color: '#ef4444',
              maxWidth: '520px',
            }}
          >
            {errorMsg}
          </p>

          <button
            className="btn btn-outline"
            style={{ marginTop: '16px' }}
            onClick={() => void fetchDocs()}
          >
            <RefreshCw size={14} />
            Retry
          </button>
        </div>
      )}

      {loadState === 'success' && docs.length === 0 && (
        <div className="placeholder-page" style={{ height: '320px' }}>
          <Inbox
            size={48}
            style={{
              color: 'var(--border-light)',
              marginBottom: '16px',
            }}
          />

          <h2>No documents yet</h2>

          <p>
            Upload an inspection report, SOP, maintenance document, or other
            supported file to get started.
          </p>

          <button
            className="btn btn-primary"
            style={{ marginTop: '18px' }}
            onClick={() => navigate('/')}
          >
            <Upload size={14} />
            Upload your first document
          </button>
        </div>
      )}

      {loadState === 'success' &&
        docs.length > 0 &&
        filteredDocs.length === 0 && (
          <div className="placeholder-page" style={{ height: '260px' }}>
            <Search
              size={40}
              style={{
                color: 'var(--border-light)',
                marginBottom: '16px',
              }}
            />

            <h2>No matching documents</h2>

            <p>
              Try a different filename or clear the search field.
            </p>

            <button
              className="btn btn-outline"
              style={{ marginTop: '16px' }}
              onClick={() => setSearchQuery('')}
            >
              Clear search
            </button>
          </div>
        )}

      {loadState === 'success' &&
        filteredDocs.length > 0 && (
          <div className="doc-library-table">
            <div className="doc-library-header">
              <span>Document</span>
              <span>Type</span>
              <span>Size</span>
              <span>Uploaded</span>
              <span>Status</span>
            </div>

            {filteredDocs.map((doc) => (
              <div
                key={doc.id}
                className="doc-library-row"
              >
                <span className="doc-library-name">
                  <FileText
                    size={16}
                    style={{
                      color: 'var(--accent-color)',
                      flexShrink: 0,
                    }}
                  />

                  <span
                    title={doc.original_filename}
                    style={{
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {doc.original_filename}
                  </span>
                </span>

                <span
                  className="doc-library-cell"
                  data-label="Type"
                >
                  {getDocumentType(doc.extension)}
                </span>

                <span
                  className="doc-library-cell"
                  data-label="Size"
                >
                  {formatBytes(doc.size_bytes)}
                </span>

                <span
                  className="doc-library-cell"
                  data-label="Uploaded"
                >
                  {formatDate(doc.created_at)}
                </span>

                <span
                  className="doc-library-cell"
                  data-label="Status"
                >
                  <span className="badge badge-success">
                    {doc.status}
                  </span>
                </span>
              </div>
            ))}
          </div>
        )}
    </div>
  );
};