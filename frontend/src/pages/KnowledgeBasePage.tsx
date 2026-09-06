import React, { useEffect, useMemo, useState } from 'react';
import {
  Database,
  FileText,
  RefreshCw,
  Upload,
  CheckCircle2,
  AlertCircle,
  Loader2,
} from 'lucide-react';
import {
  getDocuments,
  getIngestionStatus,
  ingestDocument,
  uploadDocument,
} from '../services/documentService';
import type {
  DocumentRecord,
  DocumentRole,
} from '../services/documentService';

interface IngestionState {
  status: 'idle' | 'ingesting' | 'success' | 'error';
  chunkCount?: number;
  embeddingCount?: number;
  message?: string;
}

const ROLE_OPTIONS: Array<{ value: DocumentRole; label: string }> = [
  { value: 'sop', label: 'SOP' },
  { value: 'inspection_report', label: 'Inspection Report' },
  { value: 'other', label: 'Other' },
];

const formatBytes = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

export const KnowledgeBasePage: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [selectedRole, setSelectedRole] = useState<DocumentRole>('sop');
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

    try {
      setError('');
      const result = await getDocuments();
      setDocuments(result);

      const statusEntries = await Promise.all(
        result.map(async (document) => {
          try {
            const status = await getIngestionStatus(document.id);

            if (status.chunk_count > 0 && status.embedding_count > 0) {
              return [
                document.id,
                {
                  status: 'success' as const,
                  chunkCount: status.chunk_count,
                  embeddingCount: status.embedding_count,
                  message: 'Indexed successfully.',
                },
              ] as const;
            }

            return [
              document.id,
              {
                status: 'idle' as const,
                chunkCount: status.chunk_count,
                embeddingCount: status.embedding_count,
              },
            ] as const;
          } catch {
            return null;
          }
        }),
      );

      setIngestion(
        Object.fromEntries(
          statusEntries.filter(
            (entry): entry is NonNullable<typeof entry> => entry !== null,
          ),
        ),
      );
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

  const handleUpload = async (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0];
    event.target.value = '';

    if (!file) return;

    setUploading(true);
    setError('');

    try {
      const document = await uploadDocument(file, selectedRole);

      setDocuments((current) => [
        document,
        ...current.filter((item) => item.id !== document.id),
      ]);

      await handleIngest(document.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="knowledge-page">
      <div className="page-header">
        <div>
          <div className="eyebrow">KNOWLEDGE</div>
          <h1>Knowledge Base</h1>
          <p>
            Upload organizational documents and index them for grounded AI
            retrieval.
          </p>
        </div>

        <div className="page-header-actions">
          <button
            className="secondary-button"
            type="button"
            onClick={() => void loadDocuments(true)}
            disabled={refreshing || uploading}
          >
            <RefreshCw size={16} className={refreshing ? 'spin' : undefined} />
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>

          <select
            className="knowledge-role-select"
            value={selectedRole}
            onChange={(event) =>
              setSelectedRole(event.target.value as DocumentRole)
            }
            disabled={uploading}
            aria-label="Document role"
          >
            {ROLE_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>

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
          <Database size={20} />
          <div>
            <span>Documents</span>
            <strong>{knowledgeDocuments.length}</strong>
          </div>
        </div>

        <div className="knowledge-stat">
          <FileText size={20} />
          <div>
            <span>Indexed</span>
            <strong>
              {
                Object.values(ingestion).filter(
                  (item) => item.status === 'success',
                ).length
              }
            </strong>
          </div>
        </div>
      </div>

      {error && (
        <div className="knowledge-alert error">
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="knowledge-empty">
          <Loader2 size={24} className="spin" />
          <strong>Loading knowledge base...</strong>
        </div>
      ) : knowledgeDocuments.length === 0 ? (
        <div className="knowledge-empty">
          <Database size={28} />
          <strong>No knowledge documents yet</strong>
          <span>
            Choose a document role above and add your first organizational
            document.
          </span>
        </div>
      ) : (
        <div className="knowledge-list">
          {knowledgeDocuments.map((document) => {
            const state = ingestion[document.id];

            return (
              <div className="knowledge-card" key={document.id}>
                <div className="knowledge-card-icon">
                  <FileText size={20} />
                </div>

                <div className="knowledge-card-main">
                  <div className="knowledge-card-title">
                    {document.original_filename}
                  </div>

                  <div className="knowledge-card-meta">
                    {document.role.replace('_', ' ')} Ãƒâ€šÃ‚Â·{' '}
                    {document.extension.toUpperCase().replace('.', '')} Ãƒâ€šÃ‚Â·{' '}
                    {formatBytes(document.size_bytes)}
                  </div>

                  {state?.status === 'success' && (
                    <div className="knowledge-card-status success">
                      <CheckCircle2 size={13} /> {state.message} Ãƒâ€šÃ‚Â·{' '}
                      {state.chunkCount} chunks Ãƒâ€šÃ‚Â· {state.embeddingCount}{' '}
                      embeddings
                    </div>
                  )}

                  {state?.status === 'ingesting' && (
                    <div className="knowledge-card-status ingesting">
                      <Loader2 size={13} className="spin" /> Indexing document...
                    </div>
                  )}

                  {state?.status === 'error' && (
                    <div className="knowledge-card-status error">
                      <AlertCircle size={13} /> {state.message}
                    </div>
                  )}
                </div>

                <button
                  className="knowledge-card-action"
                  type="button"
                  onClick={() => void handleIngest(document.id)}
                  disabled={state?.status === 'ingesting'}
                >
                  {state?.status === 'ingesting' ? 'Indexing...' : 'Index'}
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
