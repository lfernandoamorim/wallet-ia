import { useState, useRef, useCallback } from 'react';
import { getAccessToken } from '../services/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface UseChatStreamOptions {
  onToken?: (token: string) => void;
  onComplete?: (fullContent: string) => void;
  onError?: (error: Error) => void;
}

export function useChatStream({ onToken, onComplete, onError }: UseChatStreamOptions = {}) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [streamedContent, setStreamedContent] = useState('');
  const abortControllerRef = useRef<AbortController | null>(null);

  const startStream = useCallback(
    async (conversationId: string, message: string) => {
      setIsGenerating(true);
      setStreamedContent('');
      abortControllerRef.current = new AbortController();

      try {
        const token = getAccessToken();
        const response = await fetch(
          `${API_BASE_URL}/conversations/${conversationId}/stream`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              ...(token ? { Authorization: `Bearer ${token}` } : {}),
            },
            body: JSON.stringify({ content: message }),
            signal: abortControllerRef.current.signal,
          }
        );

        if (!response.ok) throw new Error(`Erro ao iniciar streaming: ${response.statusText}`);
        if (!response.body) throw new Error('Streaming não suportado pelo navegador');

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let accumulated = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          accumulated += chunk;
          setStreamedContent(accumulated);
          onToken?.(chunk);
        }

        onComplete?.(accumulated);
      } catch (err: unknown) {
        if ((err as Error)?.name !== 'AbortError') {
          onError?.(err instanceof Error ? err : new Error(String(err)));
        }
      } finally {
        setIsGenerating(false);
        abortControllerRef.current = null;
      }
    },
    [onToken, onComplete, onError]
  );

  const stopStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsGenerating(false);
    }
  }, []);

  return { isGenerating, streamedContent, startStream, stopStream };
}
