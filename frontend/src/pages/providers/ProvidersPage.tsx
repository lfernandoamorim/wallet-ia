import React, { useEffect, useState } from 'react';
import { KeyRound, CheckCircle2, ShieldCheck, Cpu, ExternalLink } from 'lucide-react';
import { ProviderCredential } from '../../types/provider';
import { providersService } from '../../services/providers.service';
import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';

interface ProviderCardInfo {
  id: 'openrouter' | 'openai' | 'anthropic' | 'gemini';
  name: string;
  description: string;
  docsUrl: string;
  placeholder: string;
}

const PROVIDERS_INFO: ProviderCardInfo[] = [
  {
    id: 'openrouter',
    name: 'OpenRouter',
    description: 'Acesso unificado a centenas de modelos (Llama 3, Mistral, Claude, GPT, etc.) através de uma única API key.',
    docsUrl: 'https://openrouter.ai/keys',
    placeholder: 'sk-or-v1-...',
  },
  {
    id: 'openai',
    name: 'OpenAI',
    description: 'Acesso direto aos modelos GPT-4o, GPT-4 Turbo, GPT-3.5 e modelos de embeddings.',
    docsUrl: 'https://platform.openai.com/api-keys',
    placeholder: 'sk-proj-...',
  },
  {
    id: 'anthropic',
    name: 'Anthropic Claude',
    description: 'Modelos de alta precisão com grande janela de contexto: Claude 3.5 Sonnet, Opus e Haiku.',
    docsUrl: 'https://console.anthropic.com/settings/keys',
    placeholder: 'sk-ant-api03-...',
  },
  {
    id: 'gemini',
    name: 'Google Gemini',
    description: 'Modelos multimodais de alto desempenho: Gemini 1.5 Pro e Gemini 1.5 Flash.',
    docsUrl: 'https://aistudio.google.com/app/apikey',
    placeholder: 'AIzaSy...',
  },
];

export const ProvidersPage: React.FC = () => {
  const [credentials, setCredentials] = useState<ProviderCredential[]>([]);
  const [keysInput, setKeysInput] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [savingId, setSavingId] = useState<string | null>(null);
  const [statusMap, setStatusMap] = useState<Record<string, { type: 'success' | 'error'; message: string }>>({});

  const loadCredentials = async () => {
    setIsLoading(true);
    try {
      const data = await providersService.list();
      setCredentials(data);
    } catch {
      setCredentials([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadCredentials();
  }, []);

  const handleSave = async (providerId: ProviderCardInfo['id']) => {
    const key = keysInput[providerId];
    if (!key) return;

    setSavingId(providerId);
    setStatusMap((prev) => ({ ...prev, [providerId]: undefined as any }));

    try {
      await providersService.save({
        provider: providerId,
        api_key: key,
        is_active: true,
      });

      setStatusMap((prev) => ({
        ...prev,
        [providerId]: { type: 'success', message: 'Chave salva com sucesso!' },
      }));
      setKeysInput((prev) => ({ ...prev, [providerId]: '' }));
      await loadCredentials();
    } catch (err: unknown) {
      setStatusMap((prev) => ({
        ...prev,
        [providerId]: {
          type: 'error',
          message: err instanceof Error ? err.message : 'Falha ao salvar credencial',
        },
      }));
    } finally {
      setSavingId(null);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <KeyRound className="w-7 h-7 text-indigo-400" />
          Provedores de IA & Chaves de API
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Configure suas chaves de API para permitir que os agentes consumam modelos da OpenAI, Anthropic, Gemini ou OpenRouter.
        </p>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin h-8 w-8 border-4 border-indigo-500 border-t-transparent rounded-full" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {PROVIDERS_INFO.map((info) => {
            const activeCred = credentials.find((c) => c.provider === info.id && c.is_active);
            const status = statusMap[info.id];

            return (
              <Card key={info.id} className="flex flex-col justify-between space-y-5">
                <div>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-indigo-400">
                        <Cpu className="w-5 h-5" />
                      </div>
                      <div>
                        <h3 className="text-base font-semibold text-white">{info.name}</h3>
                        <a
                          href={info.docsUrl}
                          target="_blank"
                          rel="noreferrer"
                          className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 mt-0.5"
                        >
                          <span>Obter Chave</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    </div>

                    {activeCred ? (
                      <Badge variant="success" className="flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3" />
                        Configurado
                      </Badge>
                    ) : (
                      <Badge variant="default">Não Configurado</Badge>
                    )}
                  </div>

                  <p className="mt-4 text-xs text-slate-400 leading-relaxed">{info.description}</p>
                </div>

                <div className="space-y-3 pt-3 border-t border-slate-800">
                  <div className="flex gap-2">
                    <div className="flex-1">
                      <Input
                        type="password"
                        placeholder={info.placeholder}
                        value={keysInput[info.id] || ''}
                        onChange={(e) =>
                          setKeysInput((prev) => ({ ...prev, [info.id]: e.target.value }))
                        }
                        autoComplete="off"
                      />
                    </div>
                    <Button
                      variant="primary"
                      disabled={!keysInput[info.id]}
                      isLoading={savingId === info.id}
                      onClick={() => handleSave(info.id)}
                      className="shrink-0"
                    >
                      <ShieldCheck className="w-4 h-4 mr-1.5" />
                      Salvar
                    </Button>
                  </div>

                  {status && (
                    <p
                      className={`text-xs ${
                        status.type === 'success' ? 'text-emerald-400' : 'text-red-400'
                      }`}
                    >
                      {status.message}
                    </p>
                  )}
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};
