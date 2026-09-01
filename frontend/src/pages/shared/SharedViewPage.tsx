import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Sparkles, MessageSquare, BookOpen, Bot, ArrowRight } from 'lucide-react';
import { apiFetch } from '../../services/api';
import { MessageList } from '../../components/chat/MessageList';
import { Message } from '../../types/conversation';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';

export const SharedViewPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const [data, setData] = useState<{
    type: 'conversation' | 'knowledge_base' | 'agent';
    title: string;
    description?: string;
    messages?: Message[];
    documents?: any[];
  } | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSharedResource = async () => {
      if (!slug) return;
      setIsLoading(true);
      try {
        const res = await apiFetch<any>(`/shared/${slug}`);
        setData(res);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Item compartilhado não encontrado ou expirado');
      } finally {
        setIsLoading(false);
      }
    };
    fetchSharedResource();
  }, [slug]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="animate-spin h-8 w-8 border-4 border-indigo-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4 text-center">
        <div className="w-14 h-14 rounded-2xl bg-red-950/60 border border-red-800 text-red-400 flex items-center justify-center mb-4">
          <Sparkles className="w-7 h-7" />
        </div>
        <h2 className="text-xl font-bold text-white">Conteúdo não disponível</h2>
        <p className="text-xs text-slate-400 mt-2 max-w-sm">
          {error || 'O link de compartilhamento pode estar incorreto, inativo ou restrito.'}
        </p>
        <Link to="/login" className="mt-6">
          <Button variant="primary" size="sm">
            Ir para a Wallet IA
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Header público */}
      <header className="h-16 border-b border-slate-800 bg-slate-900/80 backdrop-blur-md px-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-1.5 rounded-lg bg-gradient-to-tr from-indigo-600 to-violet-500 text-white shadow-md">
            <Sparkles className="w-5 h-5" />
          </div>
          <span className="font-bold text-lg bg-gradient-to-r from-indigo-300 to-violet-300 bg-clip-text text-transparent">
            Wallet IA
          </span>
          <Badge variant="info">Visualização Pública</Badge>
        </div>

        <Link to="/login">
          <Button variant="secondary" size="sm">
            <span>Acessar Plataforma</span>
            <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
          </Button>
        </Link>
      </header>

      {/* Conteúdo compartilhado */}
      <main className="flex-1 max-w-4xl w-full mx-auto p-6 space-y-6">
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
          <div className="flex items-center gap-2">
            {data.type === 'conversation' && <MessageSquare className="w-5 h-5 text-indigo-400" />}
            {data.type === 'knowledge_base' && <BookOpen className="w-5 h-5 text-emerald-400" />}
            {data.type === 'agent' && <Bot className="w-5 h-5 text-violet-400" />}
            <h1 className="text-xl font-bold text-white">{data.title}</h1>
          </div>
          {data.description && (
            <p className="text-xs text-slate-400">{data.description}</p>
          )}
        </div>

        {data.type === 'conversation' && data.messages && (
          <div className="rounded-2xl border border-slate-800 bg-slate-900/40 overflow-hidden">
            <MessageList messages={data.messages} />
          </div>
        )}
      </main>
    </div>
  );
};
