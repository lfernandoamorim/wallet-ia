import { render, screen, act } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ProvidersPage } from './ProvidersPage';

vi.mock('../../services/providers.service', () => ({
  providersService: {
    list: vi.fn().mockResolvedValue([]),
    save: vi.fn(),
    testConnection: vi.fn(),
  },
}));

describe('ProvidersPage', () => {
  it('renderiza os cards dos provedores OpenRouter, OpenAI, Anthropic e Gemini', async () => {
    await act(async () => {
      render(<ProvidersPage />);
    });

    expect(screen.getByText(/Provedores de IA & Chaves de API/i)).toBeInTheDocument();
    expect(screen.getByText('OpenRouter')).toBeInTheDocument();
    expect(screen.getByText('OpenAI')).toBeInTheDocument();
    expect(screen.getByText('Anthropic Claude')).toBeInTheDocument();
    expect(screen.getByText('Google Gemini')).toBeInTheDocument();
  });
});
