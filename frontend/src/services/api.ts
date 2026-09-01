const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

let accessToken: string | null = typeof window !== 'undefined' ? localStorage.getItem('wallet_ia_access_token') : null;
let refreshToken: string | null = typeof window !== 'undefined' ? localStorage.getItem('wallet_ia_refresh_token') : null;

export function setAuthTokens(access: string, refresh: string) {
  accessToken = access;
  refreshToken = refresh;
  if (typeof window !== 'undefined') {
    localStorage.setItem('wallet_ia_access_token', access);
    localStorage.setItem('wallet_ia_refresh_token', refresh);
  }
}

export function clearAuthTokens() {
  accessToken = null;
  refreshToken = null;
  if (typeof window !== 'undefined') {
    localStorage.removeItem('wallet_ia_access_token');
    localStorage.removeItem('wallet_ia_refresh_token');
  }
}

export function getAccessToken(): string | null {
  return accessToken;
}

export function getRefreshToken(): string | null {
  return refreshToken;
}

export async function apiFetch<T = unknown>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;
  const headers = new Headers(options.headers || {});

  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  if (accessToken) {
    headers.set('Authorization', `Bearer ${accessToken}`);
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (response.status === 401 && refreshToken) {
    try {
      const refreshRes = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (refreshRes.ok) {
        const data = await refreshRes.json();
        setAuthTokens(data.access_token, data.refresh_token || refreshToken);
        headers.set('Authorization', `Bearer ${data.access_token}`);
        const retryRes = await fetch(url, { ...options, headers });
        if (!retryRes.ok) throw new Error(await retryRes.text());
        return (await retryRes.json()) as T;
      }
    } catch {
      clearAuthTokens();
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
  }

  if (!response.ok) {
    const errorBody = await response.text();
    let errorMessage = `Erro HTTP ${response.status}`;
    try {
      const parsed = JSON.parse(errorBody);
      errorMessage = parsed.detail || errorMessage;
    } catch {
      // Usa mensagem padrao
    }
    throw new Error(errorMessage);
  }

  if (response.status === 204) return {} as T;
  return (await response.json()) as T;
}
