import { render, screen, act } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { KnowledgeBasesPage } from './KnowledgeBasesPage';
import { AuthProvider } from '../../contexts/AuthContext';

vi.mock('../../services/kb.service', () => ({
  kbService: {
    list: vi.fn().mockResolvedValue([]),
    create: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('KnowledgeBasesPage', () => {
  it('exibe título e botão para criar base de conhecimento', async () => {
    await act(async () => {
      render(
        <BrowserRouter>
          <AuthProvider>
            <KnowledgeBasesPage />
          </AuthProvider>
        </BrowserRouter>
      );
    });

    expect(screen.getByText(/Bases de Conhecimento/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /nova base/i })).toBeInTheDocument();
  });
});
