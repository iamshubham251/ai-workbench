import { API_BASE, fetchWithAuth } from './apiClient';

export type ApprovalDecision = 'approve' | 'reject' | 'review';

export interface ApprovalWorkflowRequest {
  instruction: string;
  document_ids: string[];
}

export interface InspectionFinding {
  finding: string;
  severity: string;
  page_number: number | null;
}

export interface ApprovalWorkflowResponse {
  workflow_id: string;
  decision: ApprovalDecision;
  summary: string;
  supporting_evidence: string[];
  findings: InspectionFinding[];
  output_path: string | null;
}

export interface WorkflowRunHistoryItem {
  id: string;
  document_id: string | null;
  document_name: string;
  status: string;
  decision: string | null;
  has_output: boolean;
  created_at: string;
  completed_at: string | null;
}

export async function executeApprovalWorkflow(
  request: ApprovalWorkflowRequest,
): Promise<ApprovalWorkflowResponse> {
  const res = await fetchWithAuth(`${API_BASE}/workflows/approval`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!res.ok) {
    const err = await res
      .json()
      .catch(() => ({ detail: res.statusText }));

    throw new Error(
      (err as { detail?: string }).detail ?? 'Approval workflow failed',
    );
  }

  return res.json() as Promise<ApprovalWorkflowResponse>;
}

export function getApprovalNoteDownloadUrl(
  outputPath: string | null,
): string | null {
  if (!outputPath) {
    return null;
  }

  const filename = outputPath.split(/[\\/]/).pop();

  if (!filename || !filename.toLowerCase().endsWith('.docx')) {
    return null;
  }

  return `${API_BASE}/workflows/approval/output/${encodeURIComponent(filename)}`;
}

export async function downloadApprovalNote(outputPath: string): Promise<void> {
  const url = getApprovalNoteDownloadUrl(outputPath);
  if (!url) {
    throw new Error('Invalid output path');
  }

  const res = await fetchWithAuth(url, {
    method: 'GET',
  });

  if (!res.ok) {
    throw new Error('Failed to download document');
  }

  const blob = await res.blob();
  const downloadUrl = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = downloadUrl;
  
  const filename = outputPath.split(/[\\/]/).pop() ?? 'download.docx';
  link.download = filename;
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(downloadUrl);
}

export async function getWorkflowHistory(): Promise<WorkflowRunHistoryItem[]> {
  const res = await fetchWithAuth(`${API_BASE}/workflows/history`);
  if (!res.ok) {
    throw new Error('Failed to load workflow history');
  }
  return res.json() as Promise<WorkflowRunHistoryItem[]>;
}
