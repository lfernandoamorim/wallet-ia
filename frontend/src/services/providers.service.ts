import { apiFetch } from './api';
import { ProviderCredential } from '../types/provider';

export interface SaveProviderPayload {
  provider: 'openrouter' | 'openai' | 'anthropic' | 'gemini';
  api_key: string;
  is_active?: boolean;
}

export const providersService = {
  async list(): Promise<ProviderCredential[]> {
    return apiFetch<ProviderCredential[]>('/providers');
  },

  async save(data: SaveProviderPayload): Promise<ProviderCredential> {
    return apiFetch<ProviderCredential>('/providers', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async testConnection(provider: string, apiKey: string): Promise<{ success: boolean; message: string }> {
    return apiFetch<{ success: boolean; message: string }>('/providers/test', {
      method: 'POST',
      body: JSON.stringify({ provider, api_key: apiKey }),
    });
  },
};
