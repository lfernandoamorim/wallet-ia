import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiFetch, setAuthTokens, clearAuthTokens, getAccessToken } from './api';

describe('API Client', () => {
  beforeEach(() => {
    clearAuthTokens();
    vi.restoreAllMocks();
  });

  it('adiciona o header Authorization quando o token está definido', async () => {
    setAuthTokens('fake_access_token', 'fake_refresh_token');
    expect(getAccessToken()).toBe('fake_access_token');

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ status: 'ok' }),
    });
    global.fetch = mockFetch;

    await apiFetch('/test');

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/test'),
      expect.objectContaining({
        headers: expect.objectContaining({
          get: expect.any(Function),
        }),
      })
    );
  });
});
