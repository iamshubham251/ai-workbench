const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api';

export interface DocumentRecord {
  id: string;
  original_filename: string;
  content_type: string;
  extension: string;
  size_bytes: number;
  status: string;
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

export async function uploadDocument(file: File): Promise<DocumentRecord> {
  const form = new FormData();
  form.append('file', file);

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
