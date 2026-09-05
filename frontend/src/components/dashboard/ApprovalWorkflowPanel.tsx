import React, { useEffect, useState } from 'react';
import {
  AlertCircle,
  CheckCircle2,
  Download,
  FileText,
  Loader2,
  Play,
  RotateCcw,
  ShieldAlert,
} from 'lucide-react';
import {
  getDocuments,
  type DocumentRecord,
} from '../../services/documentService';
import {
  executeApprovalWorkflow,
  getApprovalNoteDownloadUrl,
  type ApprovalWorkflowResponse,
} from '../../services/workflowService';

export const ApprovalWorkflowPanel: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [selectedDocumentId, setSelectedDocumentId] = useState('');
  const [instruction, setInstruction] = useState(
    'Analyze this inspection report and determine whether approval should be granted based on the available SOP evidence.',
  );
  const [result, setResult] = useState<ApprovalWorkflowResponse | null>(null);
  const [loadingDocuments, setLoadingDocuments] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState('');

  const loadDocuments = async () => {
    setLoadingDocuments(true);
    setError('');

    try {
      const records = await getDocuments();
      setDocuments(records);

      if (!selectedDocumentId && records.length > 0) {
        const firstPdf = records.find(
          (document) => document.extension.toLowerCase() === '.pdf',
        );

        if (firstPdf) {
          setSelectedDocumentId(firstPdf.id);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load documents');
    } finally {
      setLoadingDocuments(false);
    }
  };

  useEffect(() => {
    void loadDocuments();
  }, []);

  const runWorkflow = async () => {
    if (!selectedDocumentId) {
      setError('Select an inspection PDF first.');
      return;
    }

    if (!instruction.trim()) {
      setError('Enter an analysis instruction.');
      return;
    }

    setRunning(true);
    setError('');
    setResult(null);

    try {
      const response = await executeApprovalWorkflow({
        instruction: instruction.trim(),
        document_ids: [selectedDocumentId],
      });

      setResult(response);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Approval workflow failed',
      );
    } finally {
      setRunning(false);
    }
  };

  const resetWorkflow = () => {
    setResult(null);
    setError('');
    void loadDocuments();
  };

  const decisionIcon =
    result?.decision === 'approve' ? (
      <CheckCircle2 size={20} />
    ) : result?.decision === 'reject' ? (
      <ShieldAlert size={20} />
    ) : (
      <AlertCircle size={20} />
    );

  const downloadUrl = getApprovalNoteDownloadUrl(result?.output_path ?? null);

  const outputFilename = result?.output_path
    ? result.output_path.split(/[\\/]/).pop()
    : null;

  return (
    <section className="approval-workflow-panel">
      <div className="workflow-panel-header">
        <div>
          <span className="eyebrow">FLAGSHIP WORKFLOW</span>
          <h2>Inspection Approval</h2>
          <p>
            Process an inspection PDF, retrieve local SOP evidence, and generate
            an approval decision.
          </p>
        </div>

        <FileText size={28} />
      </div>

      <div className="workflow-form">
        <label>
          Inspection document

          <select
            value={selectedDocumentId}
            onChange={(event) => setSelectedDocumentId(event.target.value)}
            disabled={loadingDocuments || running}
          >
            <option value="">
              {loadingDocuments ? 'Loading documents...' : 'Select a PDF'}
            </option>

            {documents
              .filter(
                (document) =>
                  document.extension.toLowerCase() === '.pdf',
              )
              .map((document) => (
                <option key={document.id} value={document.id}>
                  {document.original_filename}
                </option>
              ))}
          </select>
        </label>

        <label>
          Analysis instruction

          <textarea
            value={instruction}
            onChange={(event) => setInstruction(event.target.value)}
            rows={4}
            disabled={running}
          />
        </label>

        {error && (
          <div className="workflow-error">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        <div className="workflow-actions">
          <button
            type="button"
            className="primary-action"
            onClick={() => void runWorkflow()}
            disabled={running || loadingDocuments || !selectedDocumentId}
          >
            {running ? (
              <>
                <Loader2 size={18} className="spin" />
                Running workflow...
              </>
            ) : (
              <>
                <Play size={18} />
                Run Approval Workflow
              </>
            )}
          </button>

          <button
            type="button"
            className="secondary-action"
            onClick={resetWorkflow}
            disabled={running}
          >
            <RotateCcw size={16} />
            Reset
          </button>
        </div>
      </div>

      {result && (
        <div className="workflow-result">
          <div className={`decision-badge decision-${result.decision}`}>
            {decisionIcon}
            <span>{result.decision.toUpperCase()}</span>
          </div>

          <div className="result-summary">
            <h3>Approval Summary</h3>
            <p>{result.summary}</p>
          </div>

          {result.supporting_evidence.length > 0 && (
            <div className="result-evidence">
              <h3>Supporting SOP Evidence</h3>

              {result.supporting_evidence.map((evidence, index) => (
                <div className="evidence-item" key={`${index}-${evidence}`}>
                  <span>{index + 1}</span>
                  <p>{evidence}</p>
                </div>
              ))}
            </div>
          )}

          {downloadUrl && outputFilename && (
            <div className="result-output">
              <FileText size={18} />

              <div>
                <strong>Approval note generated</strong>
                <span>{outputFilename}</span>
              </div>

              <a
                className="download-action"
                href={downloadUrl}
                download={outputFilename}
              >
                <Download size={16} />
                Download
              </a>
            </div>
          )}
        </div>
      )}
    </section>
  );
};
