import { render, screen, act } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from './App';

describe('App Root', () => {
  it('renderiza o fluxo de autenticação e título Wallet IA', async () => {
    await act(async () => {
      render(<App />);
    });

    expect(screen.getByText(/Wallet IA/i)).toBeInTheDocument();
  });
});
