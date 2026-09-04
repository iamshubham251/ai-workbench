import React, { useCallback, useRef, useState } from 'react';
import { UploadCloud, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';
import {
  uploadDocument,
  type DocumentRecord,
} from '../../services/documentService';

const ACCEPTED_EXTENSIONS = ['.pdf', '.docx', '.xlsx', '.pptx'];
const ACCEPTED_MIME = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation',
];
const MAX_SIZE_MB = 25;

type State =
  | { type: 'idle' }
  | { type: 'dragging' }
  | { type: 'uploading' }
  | { type: 'success'; doc: DocumentRecord }
  | { type: 'error'; message: string };

function formatBytes(bytes: number): string {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function validateFile(file: File): string | null {
  const ext = '.' + file.name.split('.').pop()?.toLowerCase();
  if (!ACCEPTED_EXTENSIONS.includes(ext)) {
    return `Unsupported file type "${ext}". Accepted: ${ACCEPTED_EXTENSIONS.join(', ')}`;
  }
  if (!ACCEPTED_MIME.includes(file.type)) {
    return `Unsupported media type. Please use PDF, DOCX, XLSX, or PPTX.`;
  }
  if (file.size === 0) {
    return 'File is empty.';
  }
  if (file.size > MAX_SIZE_MB * 1024 * 1024) {
    return `File exceeds the ${MAX_SIZE_MB} MB limit.`;
  }
  return null;
}

interface UploadDropzoneProps {
  onUploadSuccess?: (doc: DocumentRecord) => void;
}

export const UploadDropzone: React.FC<UploadDropzoneProps> = ({ onUploadSuccess }) => {
  const [state, setState] = useState<State>({ type: 'idle' });
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback(async (file: File) => {
    const err = validateFile(file);
    if (err) {
      setState({ type: 'error', message: err });
      return;
    }
    setState({ type: 'uploading' });
    try {
      const doc = await uploadDocument(file);
      setState({ type: 'success', doc });
      onUploadSuccess?.(doc);
    } catch (e) {
      setState({ type: 'error', message: e instanceof Error ? e.message : 'Upload failed' });
    }
  }, [onUploadSuccess]);

  const onDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setState({ type: 'idle' });
      const file = e.dataTransfer.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile],
  );

  const onInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFile(file);
      e.target.value = '';
    },
    [handleFile],
  );

  const reset = () => setState({ type: 'idle' });

  const isDragging = state.type === 'dragging';

  return (
    <div
      className={`upload-dropzone ${isDragging ? 'dragging' : ''} ${state.type === 'uploading' ? 'uploading' : ''}`}
      onDragOver={(e) => { e.preventDefault(); setState({ type: 'dragging' }); }}
      onDragLeave={() => setState({ type: 'idle' })}
      onDrop={onDrop}
      onClick={() => state.type === 'idle' && inputRef.current?.click()}
      role="button"
      tabIndex={0}
      aria-label="Upload document"
      onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED_EXTENSIONS.join(',')}
        style={{ display: 'none' }}
        onChange={onInputChange}
        aria-hidden="true"
      />

      {state.type === 'idle' || state.type === 'dragging' ? (
        <>
          <UploadCloud className="upload-icon" size={48} />
          <div className="upload-title">
            {isDragging ? 'Drop to upload' : 'Drop a document here'}
          </div>
          <div className="upload-subtitle">or <span className="upload-link">browse files</span></div>
          <div className="upload-formats">Accepted: PDF · DOCX · XLSX · PPTX · max {MAX_SIZE_MB} MB</div>
        </>
      ) : state.type === 'uploading' ? (
        <>
          <div className="upload-spinner" aria-live="polite" />
          <div className="upload-title" style={{ marginTop: '16px' }}>Uploading…</div>
        </>
      ) : state.type === 'success' ? (
        <>
          <CheckCircle2 size={48} style={{ color: 'var(--success-color)', marginBottom: '16px' }} />
          <div className="upload-title" style={{ color: 'var(--success-color)' }}>Upload complete</div>
          <div className="upload-result-row">
            <span className="upload-result-label">File</span>
            <span>{state.doc.original_filename}</span>
          </div>
          <div className="upload-result-row">
            <span className="upload-result-label">Type</span>
            <span>{state.doc.extension.toUpperCase().replace('.', '')}</span>
          </div>
          <div className="upload-result-row">
            <span className="upload-result-label">Size</span>
            <span>{formatBytes(state.doc.size_bytes)}</span>
          </div>
          <div className="upload-result-row">
            <span className="upload-result-label">Status</span>
            <span className="badge badge-success">{state.doc.status}</span>
          </div>
          <button className="btn btn-outline" style={{ marginTop: '16px' }} onClick={(e) => { e.stopPropagation(); reset(); }}>
            <RefreshCw size={14} /> Upload another
          </button>
        </>
      ) : (
        <>
          <AlertCircle size={48} style={{ color: '#ef4444', marginBottom: '16px' }} />
          <div className="upload-title" style={{ color: '#ef4444' }}>Upload failed</div>
          <div className="upload-subtitle" style={{ color: '#ef4444' }}>{state.message}</div>
          <button className="btn btn-outline" style={{ marginTop: '16px' }} onClick={(e) => { e.stopPropagation(); reset(); }}>
            <RefreshCw size={14} /> Try again
          </button>
        </>
      )}
    </div>
  );
};
