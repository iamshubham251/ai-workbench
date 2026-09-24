export const BACKEND_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'
).replace(/\/$/, '');

export const API_BASE = `${BACKEND_BASE_URL}/api`;

export async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const token = localStorage.getItem('auth_token');
  const headers = new Headers(options.headers || {});
  
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  
  const config = {
    ...options,
    headers,
  };
  
  const response = await fetch(url, config);
  
  if (response.status === 401) {
    localStorage.removeItem('auth_token');
    window.dispatchEvent(new Event('auth:unauthorized'));
  }
  
  return response;
}
