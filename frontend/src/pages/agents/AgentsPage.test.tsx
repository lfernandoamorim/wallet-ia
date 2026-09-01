import { render, screen, act } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { AgentsPage } from './AgentsPage';
import { AuthProvider } from '../../contexts/AuthContext';

vi.mock('../../services/agents.service', () => ({
  agentsService: {
    list: vi.fn().mockResolvedValue([]),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('AgentsPage', () => {
  it('exibe título e botão para criar novo agente', async () => {
    await act(async () => {
      render(
        <BrowserRouter>
          <AuthProvider>
            <AgentsPage />
          </AuthProvider>
        </BrowserRouter>
      );
    });

    expect(screen.getByText(/Agentes de IA/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /novo agente/i })).toBeInTheDocument();
  });
});
