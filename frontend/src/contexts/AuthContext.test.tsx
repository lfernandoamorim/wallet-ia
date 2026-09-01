import { render, screen, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { AuthProvider, useAuth } from './AuthContext';
import { authService } from '../services/auth.service';

vi.mock('../services/auth.service', () => ({
  authService: {
    login: vi.fn(),
    register: vi.fn(),
    getMe: vi.fn(),
    logout: vi.fn(),
  },
}));

vi.mock('../services/api', () => ({
  getAccessToken: vi.fn(() => null),
  apiFetch: vi.fn(),
}));

const TestAuthComponent = () => {
  const { user, isAuthenticated, login, logout, hasPermission } = useAuth();
  return (
    <div>
      <span data-testid="auth-status">{isAuthenticated ? 'logado' : 'deslogado'}</span>
      <span data-testid="user-name">{user?.full_name}</span>
      <span data-testid="has-permission">{hasPermission('agents:create') ? 'sim' : 'nao'}</span>
      <button onClick={() => login('admin@wallet.ia', 'secret123')}>Entrar</button>
      <button onClick={logout}>Sair</button>
    </div>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('inicia deslogado e efetua login com sucesso', async () => {
    const mockUser = {
      id: '1',
      email: 'admin@wallet.ia',
      full_name: 'Admin Teste',
      is_active: true,
      is_superuser: false,
      roles: ['user'],
      permissions: ['agents:create'],
      created_at: new Date().toISOString(),
    };

    vi.mocked(authService.login).mockResolvedValue({
      access_token: 'fake-token',
      refresh_token: 'fake-refresh',
      token_type: 'bearer',
    });
    vi.mocked(authService.getMe).mockResolvedValue(mockUser);

    render(
      <AuthProvider>
        <TestAuthComponent />
      </AuthProvider>
    );

    expect(screen.getByTestId('auth-status').textContent).toBe('deslogado');

    await act(async () => {
      screen.getByRole('button', { name: /entrar/i }).click();
    });

    expect(screen.getByTestId('auth-status').textContent).toBe('logado');
    expect(screen.getByTestId('user-name').textContent).toBe('Admin Teste');
    expect(screen.getByTestId('has-permission').textContent).toBe('sim');
  });
});
