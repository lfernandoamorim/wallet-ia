import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from './App';

describe('App Root', () => {
  it('renderiza o título da aplicação Wallet IA', () => {
    render(<App />);
    expect(screen.getByText(/Wallet IA — Plataforma de IA/i)).toBeInTheDocument();
  });
});
