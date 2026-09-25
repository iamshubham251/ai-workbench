import { API_BASE } from './apiClient';

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserResponse {
  id: string;
  email: string;
  is_active: boolean;
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const form = new URLSearchParams();
  form.append('username', email); // OAuth2 expects username field
  form.append('password', password);

  const res = await fetch(`${API_BASE}/auth/token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: form.toString(),
  });

  if (!res.ok) {
    throw new Error('Invalid email or password');
  }

  return res.json();
}

export async function register(email: string, password: string): Promise<UserResponse> {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? 'Registration failed');
  }

  return res.json();
}

export function logout() {
  localStorage.removeItem('auth_token');
  window.dispatchEvent(new Event('auth:unauthorized'));
}
