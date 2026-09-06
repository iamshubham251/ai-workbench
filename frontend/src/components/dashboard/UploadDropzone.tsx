import React, { useCallback, useRef, useState } from 'react';
import {
  UploadCloud,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  FileText,
} from 'lucide-react';
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
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }

  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function validateFile(file: File): string | null {
  const extension = `.${file.name.split('.').pop()?.toLowerCase()}`;

  if (!ACCEPTED_EXTENSIONS.includes(extension)) {
    return `Unsupported file type "${extension}". Accepted: ${ACCEPTED_EXTENSIONS.join(', ')}`;
  }

  if (!ACCEPTED_MIME.includes(file.type)) {
    return 'Unsupported media type. Please use PDF, DOCX, XLSX, or PPTX.';
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

export const UploadDropzone: React.FC<UploadDropzoneProps> = ({
  onUploadSuccess,
}) => {
  const [state, setState] = useState<State>({ type: 'idle' });
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback(
    async (file: File) => {
      const error = validateFile(file);

      if (error) {
        setState({ type: 'error', message: error });
        return;
      }

      setState({ type: 'uploading' });

      try {
        const document = await uploadDocument(file);

        setState({
          type: 'success',
          doc: document,
        });

        onUploadSuccess?.(document);
      } catch (error) {
        setState({
          type: 'error',
          message:
            error instanceof Error
              ? error.message
              : 'Upload failed. Please try again.',
        });
      }
    },
    [onUploadSuccess],
  );

  const onDrop = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();

      const file = event.dataTransfer.files?.[0];

      if (file) {
        void handleFile(file);
      } else {
        setState({ type: 'idle' });
      }
    },
    [handleFile],
  );

  const onInputChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];

      if (file) {
        void handleFile(file);
      }

      event.target.value = '';
    },
    [handleFile],
  );

  const reset = () => {
    setState({ type: 'idle' });
  };

  const openFilePicker = () => {
    if (state.type === 'idle') {
      inputRef.current?.click();
    }
  };

  const isDragging = state.type === 'dragging';

  return (
    <div
      className={`upload-dropzone ${isDragging ? 'dragging' : ''} ${
        state.type === 'uploading' ? 'uploading' : ''
      }`}
      onDragOver={(event) => {
        event.preventDefault();

        if (state.type !== 'uploading') {
          setState({ type: 'dragging' });
        }
      }}
      onDragLeave={() => {
        if (state.type === 'dragging') {
          setState({ type: 'idle' });
        }
      }}
      onDrop={onDrop}
      onClick={openFilePicker}
      onKeyDown={(event) => {
        if (
          (event.key === 'Enter' || event.key === ' ') &&
          state.type === 'idle'
        ) {
          event.preventDefault();
          openFilePicker();
        }
      }}
      role="button"
      tabIndex={0}
      aria-label="Upload document"
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
          <div className="upload-icon-wrap">
            <UploadCloud className="upload-icon" size={44} />
          </div>

          <div className="upload-title">
            {isDragging
              ? 'Drop your document here'
              : 'Upload a document to get started'}
          </div>

          <div className="upload-subtitle">
            Drag and drop your file here, or{' '}
            <span className="upload-link">browse files</span>
          </div>

          <div className="upload-formats">
            PDF | DOCX | XLSX | PPTX | Max {MAX_SIZE_MB} MB
          </div>

          <div className="upload-hint">
            <FileText size={14} />
            Inspection reports, SOPs, maintenance reports and other enterprise
            documents
          </div>
        </>
      ) : state.type === 'uploading' ? (
        <>
          <div className="upload-spinner" aria-hidden="true" />

          <div className="upload-title" style={{ marginTop: '16px' }}>
            Uploading document...
          </div>

          <div className="upload-subtitle">
            Storing your document securely and preparing it for processing.
          </div>
        </>
      ) : state.type === 'success' ? (
        <>
          <CheckCircle2
            size={48}
            style={{
              color: 'var(--success-color)',
              marginBottom: '16px',
            }}
          />

          <div
            className="upload-title"
            style={{ color: 'var(--success-color)' }}
          >
            Document ready
          </div>

          <div className="upload-subtitle">
            Your document has been uploaded successfully and is ready for
            processing.
          </div>

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

          <button
            className="btn btn-outline"
            style={{ marginTop: '16px' }}
            onClick={(event) => {
              event.stopPropagation();
              reset();
            }}
          >
            <RefreshCw size={14} />
            Upload another
          </button>
        </>
      ) : (
        <>
          <AlertCircle
            size={48}
            style={{
              color: '#ef4444',
              marginBottom: '16px',
            }}
          />

          <div className="upload-title" style={{ color: '#ef4444' }}>
            Upload failed
          </div>

          <div
            className="upload-subtitle"
            style={{ color: '#ef4444' }}
          >
            {state.message}
          </div>

          <button
            className="btn btn-outline"
            style={{ marginTop: '16px' }}
            onClick={(event) => {
              event.stopPropagation();
              reset();
            }}
          >
            <RefreshCw size={14} />
            Try again
          </button>
        </>
      )}
    </div>
  );
};