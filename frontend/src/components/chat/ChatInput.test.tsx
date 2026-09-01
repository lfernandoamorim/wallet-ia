import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ChatInput } from './ChatInput';

describe('ChatInput Component', () => {
  it('dispara onSend ao clicar no botão de envio', () => {
    const handleSend = vi.fn();
    render(<ChatInput onSend={handleSend} />);

    const textarea = screen.getByPlaceholderText(/envie uma mensagem/i);
    fireEvent.change(textarea, { target: { value: 'Olá assistente' } });

    const sendBtn = screen.getByRole('button', { name: /enviar mensagem/i });
    fireEvent.click(sendBtn);

    expect(handleSend).toHaveBeenCalledWith('Olá assistente');
  });

  it('exibe botão de parar quando isGenerating é true', () => {
    const handleStop = vi.fn();
    render(<ChatInput onSend={vi.fn()} onStop={handleStop} isGenerating={true} />);

    const stopBtn = screen.getByRole('button', { name: /interromper geração/i });
    expect(stopBtn).toBeInTheDocument();
    fireEvent.click(stopBtn);
    expect(handleStop).toHaveBeenCalledTimes(1);
  });
});
