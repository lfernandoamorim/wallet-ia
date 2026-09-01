import React, { useState, useEffect } from 'react';
import { Agent } from '../../types/agent';
import { Modal } from '../ui/Modal';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';

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
  const [modelName, setModelName] = useState('meta-llama/llama-3-8b-instruct');
  const [temperature, setTemperature] = useState(0.7);
  const [visibility, setVisibility] = useState<'private' | 'shared' | 'public'>('private');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialData) {
      setName(initialData.name || '');
      setDescription(initialData.description || '');
      setSystemPrompt(initialData.system_prompt || '');
      setProvider(initialData.provider || 'openrouter');
      setModelName(initialData.model_name || 'meta-llama/llama-3-8b-instruct');
      setTemperature(initialData.temperature ?? 0.7);
      setVisibility(initialData.visibility || 'private');
    } else {
      setName('');
      setDescription('');
      setSystemPrompt('Você é um assistente de IA prestativo e corporativo da Wallet IA.');
      setProvider('openrouter');
      setModelName('meta-llama/llama-3-8b-instruct');
      setTemperature(0.7);
      setVisibility('private');
    }
    setError(null);
  }, [initialData, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await onSave({
        name,
        description,
        system_prompt: systemPrompt,
        provider,
        model_name: modelName,
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
              className="w-full bg-slate-900 border border-slate-700/80 rounded-lg px-3.5 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
              value={provider}
              onChange={(e) => setProvider(e.target.value as any)}
            >
              <option value="openrouter">OpenRouter</option>
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="gemini">Google Gemini</option>
            </select>
          </div>

          <Input
            id="modelName"
            label="Identificador do Modelo"
            required
            placeholder="ex: gpt-4o, claude-3-5-sonnet, etc."
            value={modelName}
            onChange={(e) => setModelName(e.target.value)}
          />
        </div>

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
