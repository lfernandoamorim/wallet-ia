import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { useChatStream } from './useChatStream';

describe('useChatStream Hook', () => {
  it('inicializa com estado padrão e processa chunks com startStream', async () => {
    const onToken = vi.fn();
    const onComplete = vi.fn();

    const mockStream = new ReadableStream({
      start(controller) {
        controller.enqueue(new TextEncoder().encode('Olá '));
        controller.enqueue(new TextEncoder().encode('Mundo!'));
        controller.close();
      },
    });

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      body: mockStream,
    });

    const { result } = renderHook(() =>
      useChatStream({ onToken, onComplete })
    );

    expect(result.current.isGenerating).toBe(false);
    expect(result.current.streamedContent).toBe('');

    await act(async () => {
      await result.current.startStream('conv-123', 'Pergunta teste');
    });

    expect(onToken).toHaveBeenCalledTimes(2);
    expect(onComplete).toHaveBeenCalledWith('Olá Mundo!');
    expect(result.current.streamedContent).toBe('Olá Mundo!');
    expect(result.current.isGenerating).toBe(false);
  });
});
