import { apiFetch, setAuthTokens, clearAuthTokens } from './api';
import { User, AuthTokens } from '../types/auth';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const authService = {
  async login(usernameOrEmail: string, password: string): Promise<AuthTokens> {
    const formData = new URLSearchParams();
    formData.append('username', usernameOrEmail);
    formData.append('password', password);

    const res = await fetch(`${API_BASE_URL}/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData.toString(),
    });

    if (!res.ok) {
      let errorMsg = 'Falha ao autenticar';
      try {
        const err = await res.json();
        errorMsg = err.detail || errorMsg;
      } catch {
        // fallback
      }
      throw new Error(errorMsg);
    }

    const data: AuthTokens = await res.json();
    setAuthTokens(data.access_token, data.refresh_token);
    return data;
  },

  async register(email: string, password: string, full_name: string): Promise<User> {
    return apiFetch<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name }),
    });
  },

  async getMe(): Promise<User> {
    return apiFetch<User>('/users/me');
  },

  logout() {
    clearAuthTokens();
  },
};
