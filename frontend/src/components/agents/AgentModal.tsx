import React, { useState, useEffect } from 'react';
import { Agent } from '../../types/agent';
import { Modal } from '../ui/Modal';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';

export const PROVIDER_MODELS: Record<
  'openrouter' | 'openai' | 'anthropic' | 'gemini',
  Array<{ id: string; label: string }>
> = {
  openrouter: [
    // OpenAI (incluindo gpt-4.1-mini como padrão)
    { id: 'openai/gpt-4.1-mini', label: 'OpenAI: GPT-4.1 Mini (Padrão Recomendado)' },
    { id: 'openai/gpt-4.1', label: 'OpenAI: GPT-4.1' },
    { id: 'openai/gpt-4o', label: 'OpenAI: GPT-4o' },
    { id: 'openai/gpt-4o-mini', label: 'OpenAI: GPT-4o Mini' },
    { id: 'openai/o3-mini', label: 'OpenAI: o3-mini (Reasoning)' },
    { id: 'openai/o1', label: 'OpenAI: o1 (Reasoning)' },
    // Google Gemini
    { id: 'google/gemini-2.5-pro', label: 'Google: Gemini 2.5 Pro' },
    { id: 'google/gemini-2.0-flash-001', label: 'Google: Gemini 2.0 Flash' },
    { id: 'google/gemini-2.0-flash-thinking-exp-01-21', label: 'Google: Gemini 2.0 Flash Thinking' },
    { id: 'google/gemini-pro-1.5', label: 'Google: Gemini 1.5 Pro' },
    { id: 'google/gemini-flash-1.5', label: 'Google: Gemini 1.5 Flash' },
    // Anthropic Claude
    { id: 'anthropic/claude-3.7-sonnet', label: 'Anthropic: Claude 3.7 Sonnet (Hybrid Reasoning)' },
    { id: 'anthropic/claude-3.5-sonnet', label: 'Anthropic: Claude 3.5 Sonnet' },
    { id: 'anthropic/claude-3.5-haiku', label: 'Anthropic: Claude 3.5 Haiku' },
    { id: 'anthropic/claude-3-opus', label: 'Anthropic: Claude 3 Opus' },
    // Kimi (Moonshot AI)
    { id: 'moonshotai/kimi-k1.5', label: 'Kimi: Moonshot Kimi K1.5' },
    { id: 'moonshotai/moonshot-v1-128k', label: 'Kimi: Moonshot v1 (128k context)' },
    { id: 'moonshotai/moonshot-v1-32k', label: 'Kimi: Moonshot v1 (32k context)' },
    { id: 'moonshotai/moonshot-v1-8k', label: 'Kimi: Moonshot v1 (8k context)' },
    // Meta Llama
    { id: 'meta-llama/llama-3.3-70b-instruct', label: 'Meta: Llama 3.3 70B Instruct' },
    { id: 'meta-llama/llama-3.1-405b-instruct', label: 'Meta: Llama 3.1 405B Instruct' },
    { id: 'meta-llama/llama-3.1-70b-instruct', label: 'Meta: Llama 3.1 70B Instruct' },
    { id: 'meta-llama/llama-3.1-8b-instruct', label: 'Meta: Llama 3.1 8B Instruct' },
    { id: 'meta-llama/llama-3-8b-instruct', label: 'Meta: Llama 3 8B Instruct' },
    // DeepSeek, Qwen & Mistral
    { id: 'deepseek/deepseek-r1', label: 'DeepSeek: DeepSeek R1 (Reasoning)' },
    { id: 'deepseek/deepseek-chat', label: 'DeepSeek: DeepSeek V3 (Chat)' },
    { id: 'qwen/qwen-2.5-72b-instruct', label: 'Qwen: Qwen 2.5 72B Instruct' },
    { id: 'mistralai/mistral-large-2407', label: 'Mistral: Mistral Large 2' },
  ],
  openai: [
    { id: 'gpt-4.1-mini', label: 'GPT-4.1 Mini (Padrão Recomendado)' },
    { id: 'gpt-4.1', label: 'GPT-4.1' },
    { id: 'gpt-4o', label: 'GPT-4o (Multimodal & Rápido)' },
    { id: 'gpt-4o-mini', label: 'GPT-4o Mini (Econômico)' },
    { id: 'o3-mini', label: 'o3-mini (Raciocínio Rápido)' },
    { id: 'o1', label: 'o1 (Raciocínio Avançado)' },
    { id: 'o1-mini', label: 'o1-mini (Raciocínio Leve)' },
    { id: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
    { id: 'gpt-4', label: 'GPT-4' },
    { id: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
  ],
  anthropic: [
    { id: 'claude-3-7-sonnet-20250219', label: 'Claude 3.7 Sonnet (Hybrid Reasoning)' },
    { id: 'claude-3-5-sonnet-20241022', label: 'Claude 3.5 Sonnet (Recomendado)' },
    { id: 'claude-3-5-haiku-20241022', label: 'Claude 3.5 Haiku (Rápido)' },
    { id: 'claude-3-opus-20240229', label: 'Claude 3 Opus (Alta complexidade)' },
    { id: 'claude-3-haiku-20240307', label: 'Claude 3 Haiku' },
  ],
  gemini: [
    { id: 'gemini-2.5-pro', label: 'Gemini 2.5 Pro (Próxima Geração)' },
    { id: 'gemini-2.0-flash', label: 'Gemini 2.0 Flash (Última Geração)' },
    { id: 'gemini-2.0-flash-thinking-exp-01-21', label: 'Gemini 2.0 Flash Thinking' },
    { id: 'gemini-2.0-pro-exp-02-05', label: 'Gemini 2.0 Pro Experimental' },
    { id: 'gemini-1.5-pro', label: 'Gemini 1.5 Pro (Janela 2M tokens)' },
    { id: 'gemini-1.5-flash', label: 'Gemini 1.5 Flash (Rápido)' },
    { id: 'gemini-1.0-pro', label: 'Gemini 1.0 Pro' },
  ],
};

function getDefaultModelForProvider(p: 'openrouter' | 'openai' | 'anthropic' | 'gemini'): string {
  if (p === 'openrouter') return 'openai/gpt-4.1-mini';
  if (p === 'openai') return 'gpt-4.1-mini';
  return PROVIDER_MODELS[p][0]?.id || '';
}

interface AgentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: Partial<Agent>) => Promise<void>;
  initialData?: Agent | null;
}

export const AgentModal: React.FC<AgentModalProps> = ({
  isOpen,
  onClose,
  onSave,
  initialData,
}) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [systemPrompt, setSystemPrompt] = useState('');
  const [provider, setProvider] = useState<'openrouter' | 'openai' | 'anthropic' | 'gemini'>('openrouter');
  const [modelName, setModelName] = useState('openai/gpt-4.1-mini');
  const [isCustomModel, setIsCustomModel] = useState(false);
  const [temperature, setTemperature] = useState(0.7);
  const [visibility, setVisibility] = useState<'private' | 'shared' | 'public'>('private');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialData) {
      const p = (initialData.provider || 'openrouter') as 'openrouter' | 'openai' | 'anthropic' | 'gemini';
      const defaultM = getDefaultModelForProvider(p);
      const m = initialData.model || initialData.model_name || defaultM;
      setName(initialData.name || '');
      setDescription(initialData.description || '');
      setSystemPrompt(initialData.system_prompt || '');
      setProvider(p);
      setModelName(m);
      const isKnown = (PROVIDER_MODELS[p] || []).some((item) => item.id.toLowerCase() === m.toLowerCase());
      setIsCustomModel(!isKnown);
      setTemperature(initialData.temperature ?? 0.7);
      setVisibility(initialData.visibility || 'private');
    } else {
      setName('');
      setDescription('');
      setSystemPrompt('Você é um assistente de IA prestativo e corporativo da Wallet IA.');
      setProvider('openrouter');
      setModelName(getDefaultModelForProvider('openrouter'));
      setIsCustomModel(false);
      setTemperature(0.7);
      setVisibility('private');
    }
    setError(null);
  }, [initialData, isOpen]);

  const handleProviderChange = (newProvider: 'openrouter' | 'openai' | 'anthropic' | 'gemini') => {
    setProvider(newProvider);
    setIsCustomModel(false);
    const defaultModel = getDefaultModelForProvider(newProvider);
    setModelName(defaultModel);
  };

  const handleModelSelectChange = (value: string) => {
    if (value === '__custom__') {
      setIsCustomModel(true);
      setModelName('');
    } else {
      setIsCustomModel(false);
      setModelName(value);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!modelName.trim()) {
      setError('Por favor, selecione ou informe o identificador do modelo.');
      return;
    }
    setError(null);
    setIsLoading(true);

    try {
      await onSave({
        name,
        description,
        system_prompt: systemPrompt,
        provider,
        model: modelName.trim(),
        temperature: Number(temperature),
        visibility,
        knowledge_base_ids: initialData?.knowledge_base_ids || [],
      });
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Falha ao salvar agente');
    } finally {
      setIsLoading(false);
    }
  };

  const currentModels = PROVIDER_MODELS[provider] || [];

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={initialData ? 'Editar Agente de IA' : 'Novo Agente de IA'}
      maxWidth="max-w-xl"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 rounded-lg bg-red-950/60 border border-red-800 text-red-300 text-xs">
            {error}
          </div>
        )}

        <Input
          id="agentName"
          label="Nome do Agente"
          required
          placeholder="ex: Assistente Financeiro, Suporte N1"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />

        <Input
          id="agentDesc"
          label="Descrição Resumida"
          placeholder="ex: Agente focado em análise de planilhas e relatórios"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />

        <div className="space-y-1.5">
          <label htmlFor="systemPrompt" className="block text-xs font-medium text-slate-300">
            System Prompt (Instruções e Persona)
          </label>
          <textarea
            id="systemPrompt"
            required
            rows={4}
            className="w-full bg-slate-900 border border-slate-700/80 rounded-lg px-3.5 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors font-mono"
            placeholder="Defina aqui como o modelo deve se comportar..."
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <label htmlFor="providerSelect" className="block text-xs font-medium text-slate-300">
              Provedor
            </label>
            <select
              id="providerSelect"
              className="w-full bg-slate-900 border border-slate-700/80 rounded-lg px-3.5 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors cursor-pointer"
              value={provider}
              onChange={(e) => handleProviderChange(e.target.value as any)}
            >
              <option value="openrouter">OpenRouter</option>
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="gemini">Google Gemini</option>
            </select>
          </div>

          <div className="space-y-1.5">
            <label htmlFor="modelSelect" className="block text-xs font-medium text-slate-300">
              Identificador do Modelo
            </label>
            <select
              id="modelSelect"
              className="w-full bg-slate-900 border border-slate-700/80 rounded-lg px-3.5 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors cursor-pointer"
              value={isCustomModel ? '__custom__' : modelName}
              onChange={(e) => handleModelSelectChange(e.target.value)}
            >
              {currentModels.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.label} ({m.id})
                </option>
              ))}
              <option value="__custom__">Outro (digitar manualmente)...</option>
            </select>
          </div>
        </div>

        {isCustomModel && (
          <div className="animate-in fade-in duration-200">
            <Input
              id="customModelInput"
              label="Nome / Identificador do Modelo Personalizado"
              required
              placeholder="ex: mistralai/mixtral-8x7b-instruct, gpt-4o-2024-08-06"
              value={modelName}
              onChange={(e) => setModelName(e.target.value)}
            />
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label htmlFor="temperatureRange" className="block text-xs font-medium text-slate-300">
                Temperatura: {temperature}
              </label>
            </div>
            <input
              id="temperatureRange"
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={temperature}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
              className="w-full accent-indigo-500 cursor-pointer"
            />
          </div>

          <div className="space-y-1.5">
            <label htmlFor="visibilitySelect" className="block text-xs font-medium text-slate-300">
              Visibilidade
            </label>
            <select
              id="visibilitySelect"
              className="w-full bg-slate-900 border border-slate-700/80 rounded-lg px-3.5 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
              value={visibility}
              onChange={(e) => setVisibility(e.target.value as any)}
            >
              <option value="private">Privado (Apenas eu)</option>
              <option value="shared">Compartilhado (Equipe autenticada)</option>
              <option value="public">Público (Link externo)</option>
            </select>
          </div>
        </div>

        <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" variant="primary" isLoading={isLoading}>
            {initialData ? 'Salvar Alterações' : 'Criar Agente'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};
