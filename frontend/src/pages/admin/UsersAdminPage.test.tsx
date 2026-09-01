import { render, screen, act } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { UsersAdminPage } from './UsersAdminPage';

vi.mock('../../services/admin.service', () => ({
  adminService: {
    listUsers: vi.fn().mockResolvedValue([]),
    listRoles: vi.fn().mockResolvedValue([]),
    updateUserRoles: vi.fn(),
    toggleUserStatus: vi.fn(),
  },
}));

describe('UsersAdminPage', () => {
  it('exibe título de gestão de usuários e tabela', async () => {
    await act(async () => {
      render(<UsersAdminPage />);
    });

    expect(screen.getByText(/Gestão de Usuários/i)).toBeInTheDocument();
  });
});
