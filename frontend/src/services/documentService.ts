const BACKEND_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'
).replace(/\/$/, '');

const API_BASE = `${BACKEND_BASE_URL}/api`;

export type DocumentRole = 'inspection_report' | 'sop' | 'other';

export interface DocumentRecord {
  id: string;
  original_filename: string;
  content_type: string;
  extension: string;
  size_bytes: number;
  status: string;
  role: DocumentRole;
  created_at: string;
  updated_at: string;
}

export interface UploadError {
  detail: string;
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error((err as UploadError).detail ?? 'Request failed');
  }
  return res.json() as Promise<T>;
}

export async function uploadDocument(
  file: File,
  role: DocumentRole = 'other',
): Promise<DocumentRecord> {
  const form = new FormData();
  form.append('file', file);
  form.append('role', role);

  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: form,
  });
  return handleResponse<DocumentRecord>(res);
}

export async function getDocuments(): Promise<DocumentRecord[]> {
  const res = await fetch(`${API_BASE}/documents`);
  return handleResponse<DocumentRecord[]>(res);
}

export async function getDocument(id: string): Promise<DocumentRecord> {
  const res = await fetch(`${API_BASE}/documents/${id}`);
  return handleResponse<DocumentRecord>(res);
}

export async function deleteDocument(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/documents/${id}`, { method: 'DELETE' });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error((err as UploadError).detail ?? 'Delete failed');
  }
}

export interface KnowledgeIngestionResponse {
  document_id: string;
  chunk_count: number;
  embedding_count: number;
}

export async function ingestDocument(
  id: string,
): Promise<KnowledgeIngestionResponse> {
  const res = await fetch(`${API_BASE}/knowledge/${id}/ingest`, {
    method: 'POST',
  });
  return handleResponse<KnowledgeIngestionResponse>(res);
}

export async function getIngestionStatus(
  id: string,
): Promise<KnowledgeIngestionResponse> {
  const res = await fetch(`${API_BASE}/knowledge/${id}/status`);
  return handleResponse<KnowledgeIngestionResponse>(res);
}
