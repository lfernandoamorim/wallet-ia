export interface Agent {
  id: string;
  name: string;
  description?: string;
  avatar_url?: string;
  system_prompt: string;
  provider: 'openrouter' | 'openai' | 'anthropic' | 'gemini';
  model: string;
  model_name?: string;
  temperature: number;
  max_tokens?: number;
  visibility: 'private' | 'shared' | 'public';
  public_slug?: string;
  knowledge_base_ids: string[];
  created_at: string;
}
