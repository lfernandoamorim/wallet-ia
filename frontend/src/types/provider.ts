export interface ProviderCredential {
  id: string;
  provider: 'openrouter' | 'openai' | 'anthropic' | 'gemini';
  is_active: boolean;
  is_global: boolean;
  created_at: string;
}
