import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { AuthProvider } from '../../contexts/AuthContext';

describe('Sidebar Component', () => {
  it('exibe links de navegação para Chat, Agentes e Bases', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Sidebar />
        </AuthProvider>
      </BrowserRouter>
    );

    expect(screen.getByText(/chat/i)).toBeInTheDocument();
    expect(screen.getByText(/agentes/i)).toBeInTheDocument();
    expect(screen.getByText(/base de conhecimento/i)).toBeInTheDocument();
  });
});
