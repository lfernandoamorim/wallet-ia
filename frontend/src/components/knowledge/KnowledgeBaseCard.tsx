import React from 'react';
import { BookOpen, FileText, Trash2, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { KnowledgeBase } from '../../types/knowledge';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';

interface KnowledgeBaseCardProps {
  kb: KnowledgeBase;
  onDelete: (id: string) => void;
}

export const KnowledgeBaseCard: React.FC<KnowledgeBaseCardProps> = ({ kb, onDelete }) => {
  const navigate = useNavigate();

  const visibilityVariants = {
    private: 'default' as const,
    shared: 'info' as const,
    public: 'success' as const,
  };

  const visibilityLabels = {
    private: 'Privada',
    shared: 'Compartilhada',
    public: 'Pública',
  };

  return (
    <Card className="flex flex-col justify-between hover:border-indigo-500/50 transition-all duration-200 group">
      <div>
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600/30 to-teal-600/30 border border-emerald-500/30 flex items-center justify-center text-emerald-400 group-hover:scale-105 transition-transform">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-100 group-hover:text-emerald-300 transition-colors text-base">
                {kb.name}
              </h3>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant={visibilityVariants[kb.visibility]}>
                  {visibilityLabels[kb.visibility]}
                </Badge>
                <span className="text-[11px] text-slate-500">
                  {kb.embedding_model || 'text-embedding-3-small'}
                </span>
              </div>
            </div>
          </div>

          <button
            onClick={() => onDelete(kb.id)}
            className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-red-950/40 rounded-lg transition-colors cursor-pointer"
            aria-label="Excluir Base de Conhecimento"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>

        <p className="mt-3 text-xs text-slate-400 line-clamp-2 leading-relaxed">
          {kb.description || 'Nenhuma descrição informada.'}
        </p>

        <div className="mt-4 flex items-center gap-2 text-xs text-slate-300">
          <FileText className="w-4 h-4 text-slate-500" />
          <span>{kb.document_count ?? 0} documento(s) indexado(s)</span>
        </div>
      </div>

      <div className="mt-5 pt-3 border-t border-slate-800/80 flex items-center justify-between">
        <span className="text-[11px] text-slate-500">
          Criado em: {new Date(kb.created_at || Date.now()).toLocaleDateString('pt-BR')}
        </span>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => navigate(`/knowledge/${kb.id}`)}
          className="hover:bg-emerald-600 hover:text-white hover:border-transparent transition-all"
        >
          <span>Gerenciar</span>
          <ArrowRight className="w-3.5 h-3.5 ml-1" />
        </Button>
      </div>
    </Card>
  );
};
