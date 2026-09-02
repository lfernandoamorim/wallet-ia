import React from 'react';
import { Bot, Edit2, Trash2, Cpu, MessageSquare } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Agent } from '../../types/agent';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';

interface AgentCardProps {
  agent: Agent;
  onEdit: (agent: Agent) => void;
  onDelete: (agentId: string) => void;
}

export const AgentCard: React.FC<AgentCardProps> = ({ agent, onEdit, onDelete }) => {
  const navigate = useNavigate();

  const visibilityVariants = {
    private: 'default' as const,
    shared: 'info' as const,
    public: 'success' as const,
  };

  const visibilityLabels = {
    private: 'Privado',
    shared: 'Compartilhado',
    public: 'Público',
  };

  return (
    <Card className="flex flex-col justify-between hover:border-indigo-500/50 transition-all duration-200 group">
      <div>
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600/30 to-violet-600/30 border border-indigo-500/30 flex items-center justify-center text-indigo-400 group-hover:scale-105 transition-transform">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-100 group-hover:text-indigo-300 transition-colors text-base">
                {agent.name}
              </h3>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant={visibilityVariants[agent.visibility]}>
                  {visibilityLabels[agent.visibility]}
                </Badge>
                <span className="text-[11px] text-slate-400 flex items-center gap-1">
                  <Cpu className="w-3 h-3 text-slate-500" />
                  {agent.provider.toUpperCase()} / {agent.model || agent.model_name}
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={() => onEdit(agent)}
              className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors cursor-pointer"
              aria-label="Editar Agente"
            >
              <Edit2 className="w-4 h-4" />
            </button>
            <button
              onClick={() => onDelete(agent.id)}
              className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-red-950/40 rounded-lg transition-colors cursor-pointer"
              aria-label="Excluir Agente"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        <p className="mt-3 text-xs text-slate-400 line-clamp-2 leading-relaxed">
          {agent.description || agent.system_prompt || 'Nenhuma descrição fornecida.'}
        </p>

        {agent.knowledge_base_ids && agent.knowledge_base_ids.length > 0 && (
          <div className="mt-3 flex items-center gap-1.5 text-[11px] text-indigo-300 bg-indigo-950/40 px-2.5 py-1 rounded-md border border-indigo-900/40 w-fit">
            <span>{agent.knowledge_base_ids.length} base(s) de conhecimento vinculada(s)</span>
          </div>
        )}
      </div>

      <div className="mt-5 pt-3 border-t border-slate-800/80 flex items-center justify-between">
        <span className="text-[11px] text-slate-400">Temp: {agent.temperature}</span>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => navigate(`/chat?agent=${agent.id}`)}
          className="hover:bg-indigo-600 hover:text-white hover:border-transparent transition-all"
        >
          <MessageSquare className="w-3.5 h-3.5 mr-1" />
          Conversar
        </Button>
      </div>
    </Card>
  );
};
