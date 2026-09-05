const BACKEND_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'
).replace(/\/$/, '');

const API_BASE = `${BACKEND_BASE_URL}/api`;

export type ApprovalDecision = 'approve' | 'reject' | 'review';

export interface ApprovalWorkflowRequest {
  instruction: string;
  document_ids: string[];
}

export interface ApprovalWorkflowResponse {
  workflow_id: string;
  decision: ApprovalDecision;
  summary: string;
  supporting_evidence: string[];
  output_path: string | null;
}

export async function executeApprovalWorkflow(
  request: ApprovalWorkflowRequest,
): Promise<ApprovalWorkflowResponse> {
  const res = await fetch(`${API_BASE}/workflows/approval`, {
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
