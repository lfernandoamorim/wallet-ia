import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Button } from './Button';

describe('Button Component', () => {
  it('renderiza o botão com estilo primário e dispara evento onClick', () => {
    const handleClick = vi.fn();
    render(<Button variant="primary" onClick={handleClick}>Enviar</Button>);
    const btn = screen.getByRole('button', { name: /enviar/i });
    expect(btn).toBeInTheDocument();
    fireEvent.click(btn);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('desabilita o botão quando isLoading é true', () => {
    render(<Button isLoading>Processando</Button>);
    const btn = screen.getByRole('button', { name: /processando/i });
    expect(btn).toBeDisabled();
    expect(screen.getByTestId('spinner')).toBeInTheDocument();
  });
});
