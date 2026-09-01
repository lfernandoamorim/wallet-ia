import React, { useEffect, useState } from 'react';
import { Plus, Search, Bot } from 'lucide-react';
import { Agent } from '../../types/agent';
import { agentsService } from '../../services/agents.service';
import { AgentCard } from '../../components/agents/AgentCard';
import { AgentModal } from '../../components/agents/AgentModal';
import { Button } from '../../components/ui/Button';

export const AgentsPage: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [search, setSearch] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingAgent, setEditingAgent] = useState<Agent | null>(null);

  const fetchAgents = async () => {
    setIsLoading(true);
    try {
      const data = await agentsService.list();
      setAgents(data);
    } catch {
      setAgents([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAgents();
  }, []);

  const handleSave = async (data: Partial<Agent>) => {
    if (editingAgent) {
      await agentsService.update(editingAgent.id, data);
    } else {
      await agentsService.create(data);
    }
    await fetchAgents();
  };

  const handleDelete = async (agentId: string) => {
    if (confirm('Tem certeza que deseja excluir este agente?')) {
      await agentsService.delete(agentId);
      await fetchAgents();
    }
  };

  const filteredAgents = agents.filter(
    (a) =>
      a.name.toLowerCase().includes(search.toLowerCase()) ||
      (a.description && a.description.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <Bot className="w-7 h-7 text-indigo-400" />
            Agentes de IA
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Crie, personalize e gerencie agentes com personas e bases de conhecimento específicas.
          </p>
        </div>

        <Button
          onClick={() => {
            setEditingAgent(null);
            setIsModalOpen(true);
          }}
          variant="primary"
          className="shadow-lg shadow-indigo-600/20"
        >
          <Plus className="w-4 h-4 mr-1.5" />
          Novo Agente
        </Button>
      </div>

      {/* Filter Bar */}
      <div className="relative">
        <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          placeholder="Buscar agentes por nome ou descrição..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
        />
      </div>

      {/* Grid */}
      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin h-8 w-8 border-4 border-indigo-500 border-t-transparent rounded-full" />
        </div>
      ) : filteredAgents.length === 0 ? (
        <div className="text-center py-16 px-4 border border-dashed border-slate-800 rounded-2xl bg-slate-900/30">
          <Bot className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-slate-300">Nenhum agente encontrado</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            {search ? 'Nenhum resultado corresponde à sua pesquisa.' : 'Crie seu primeiro agente para começar a automatizar tarefas com IA.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredAgents.map((agent) => (
            <AgentCard
              key={agent.id}
              agent={agent}
              onEdit={(a) => {
                setEditingAgent(a);
                setIsModalOpen(true);
              }}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}

      <AgentModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSave}
        initialData={editingAgent}
      />
    </div>
  );
};
