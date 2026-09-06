import React, { useEffect, useMemo, useState } from 'react';
import { Database, FileText, RefreshCw, Upload, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import {
  getDocuments,
  ingestDocument,
  uploadDocument,
} from '../services/documentService';
import type { DocumentRecord } from '../services/documentService';

interface IngestionState {
  status: 'idle' | 'ingesting' | 'success' | 'error';
  chunkCount?: number;
  embeddingCount?: number;
  message?: string;
}

export const KnowledgeBasePage: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [ingestion, setIngestion] = useState<Record<string, IngestionState>>({});

  const knowledgeDocuments = useMemo(
    () => documents.filter((document) => document.status !== 'failed'),
    [documents],
  );

  const loadDocuments = async (isRefresh = false) => {
    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    setError('');

    try {
      const result = await getDocuments();
      setDocuments(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load documents.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    void loadDocuments();
  }, []);

  const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = '';

    if (!file) return;

    setUploading(true);
    setError('');

    try {
      const document = await uploadDocument(file);

      setDocuments((current) => [
        document,
        ...current.filter((item) => item.id !== document.id),
      ]);

      await handleIngest(document.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Knowledge document upload failed.');
    } finally {
      setUploading(false);
    }
  };

  const handleIngest = async (documentId: string) => {
    setIngestion((current) => ({
      ...current,
      [documentId]: { status: 'ingesting' },
    }));

    try {
      const result = await ingestDocument(documentId);

      setIngestion((current) => ({
        ...current,
        [documentId]: {
          status: 'success',
          chunkCount: result.chunk_count,
          embeddingCount: result.embedding_count,
          message: 'Indexed and ready for retrieval',
        },
      }));
    } catch (err) {
      setIngestion((current) => ({
        ...current,
        [documentId]: {
          status: 'error',
          message: err instanceof Error ? err.message : 'Ingestion failed.',
        },
      }));
    }
  };

  return (
    <div className="knowledge-page">
      <div className="page-header">
        <div>
          <div className="eyebrow">KNOWLEDGE</div>
          <h1>Knowledge Base</h1>
          <p>
            Upload organizational documents and index them for grounded AI retrieval.
          </p>
        </div>

        <div className="page-header-actions">
          <button
            className="secondary-button"
            type="button"
            onClick={() => void loadDocuments(true)}
            disabled={loading || refreshing}
          >
            <RefreshCw size={16} className={refreshing ? 'spin' : undefined} />
            Refresh
          </button>

          <label className="primary-button">
            <Upload size={16} />
            {uploading ? 'Uploading...' : 'Add Knowledge'}
            <input
              type="file"
              accept=".pdf,.docx,.xlsx,.pptx"
              onChange={handleUpload}
              disabled={uploading}
              hidden
            />
          </label>
        </div>
      </div>

      <div className="knowledge-overview">
        <div className="knowledge-stat">
          <Database size={18} />
          <div>
            <span>Documents</span>
            <strong>{knowledgeDocuments.length}</strong>
          </div>
        </div>

        <div className="knowledge-stat">
          <FileText size={18} />
          <div>
            <span>Indexed</span>
            <strong>
              {Object.values(ingestion).filter((item) => item.status === 'success').length}
            </strong>
          </div>
        </div>
      </div>

      {error && (
        <div className="knowledge-alert error">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="knowledge-empty">
          <Loader2 size={28} className="spin" />
          <p>Loading knowledge base...</p>
        </div>
      ) : knowledgeDocuments.length === 0 ? (
        <div className="knowledge-empty">
          <Database size={42} />
          <h2>No knowledge documents yet</h2>
          <p>
            Add a company SOP, safety policy, maintenance guide, or inspection guideline
            to make it available to grounded AI workflows.
          </p>
          <label className="primary-button">
            <Upload size={16} />
            Add Knowledge Document
            <input
              type="file"
              accept=".pdf,.docx,.xlsx,.pptx"
              onChange={handleUpload}
              disabled={uploading}
              hidden
            />
          </label>
        </div>
      ) : (
        <div className="knowledge-list">
          {knowledgeDocuments.map((document) => {
            const state = ingestion[document.id];

            return (
              <div className="knowledge-card" key={document.id}>
                <div className="knowledge-card-icon">
                  <FileText size={22} />
                </div>

                <div className="knowledge-card-main">
                  <h3>{document.original_filename}</h3>
                  <p>
                    {document.extension.toUpperCase()} ·{' '}
                    {(document.size_bytes / 1024).toFixed(1)} KB
                  </p>

                  {state?.status === 'success' && (
                    <div className="knowledge-meta success">
                      <CheckCircle2 size={15} />
                      {state.message} · {state.chunkCount} chunks · {state.embeddingCount} embeddings
                    </div>
                  )}

                  {state?.status === 'ingesting' && (
                    <div className="knowledge-meta">
                      <Loader2 size={15} className="spin" />
                      Indexing document...
                    </div>
                  )}

                  {state?.status === 'error' && (
                    <div className="knowledge-meta error">
                      <AlertCircle size={15} />
                      {state.message}
                    </div>
                  )}
                </div>

                <div className="knowledge-card-action">
                  <button
                    className="secondary-button"
                    type="button"
                    onClick={() => void handleIngest(document.id)}
                    disabled={state?.status === 'ingesting'}
                  >
                    {state?.status === 'ingesting' ? 'Indexing...' : 'Index'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
