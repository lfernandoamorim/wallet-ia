import React, { useEffect, useState } from 'react';
import { Plus, Search, BookOpen } from 'lucide-react';
import { KnowledgeBase } from '../../types/knowledge';
import { kbService } from '../../services/kb.service';
import { KnowledgeBaseCard } from '../../components/knowledge/KnowledgeBaseCard';
import { Modal } from '../../components/ui/Modal';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';

export const KnowledgeBasesPage: React.FC = () => {
  const [kbs, setKbs] = useState<KnowledgeBase[]>([]);
  const [search, setSearch] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Form states
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [visibility, setVisibility] = useState<'private' | 'shared' | 'public'>('private');
  const [embeddingModel, setEmbeddingModel] = useState('text-embedding-3-small');
  const [isSaving, setIsSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const fetchKbs = async () => {
    setIsLoading(true);
    try {
      const data = await kbService.list();
      setKbs(data);
    } catch {
      setKbs([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchKbs();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setIsSaving(true);

    try {
      await kbService.create({
        name,
        description,
        visibility,
        embedding_model: embeddingModel,
      });
      setIsModalOpen(false);
      setName('');
      setDescription('');
      await fetchKbs();
    } catch (err: unknown) {
      setFormError(err instanceof Error ? err.message : 'Falha ao criar base');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Tem certeza que deseja excluir esta base de conhecimento e todos os seus documentos indexados?')) {
      await kbService.delete(id);
      await fetchKbs();
    }
  };

  const filtered = kbs.filter(
    (k) =>
      k.name.toLowerCase().includes(search.toLowerCase()) ||
      (k.description && k.description.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <BookOpen className="w-7 h-7 text-emerald-400" />
            Bases de Conhecimento (RAG)
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Centralize documentos, manuais e planilhas para enriquecer o contexto das respostas dos seus agentes.
          </p>
        </div>

        <Button
          onClick={() => {
            setName('');
            setDescription('');
            setFormError(null);
            setIsModalOpen(true);
          }}
          variant="primary"
          className="bg-emerald-600 hover:bg-emerald-500 shadow-lg shadow-emerald-600/20"
        >
          <Plus className="w-4 h-4 mr-1.5" />
          Nova Base
        </Button>
      </div>

      <div className="relative">
        <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          placeholder="Buscar bases de conhecimento por nome..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-colors"
        />
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin h-8 w-8 border-4 border-emerald-500 border-t-transparent rounded-full" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-16 px-4 border border-dashed border-slate-800 rounded-2xl bg-slate-900/30">
          <BookOpen className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-slate-300">Nenhuma base de conhecimento encontrada</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            {search ? 'Nenhum resultado corresponde à sua pesquisa.' : 'Crie sua primeira base de conhecimento para carregar documentos.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filtered.map((kb) => (
            <KnowledgeBaseCard key={kb.id} kb={kb} onDelete={handleDelete} />
          ))}
        </div>
      )}

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Nova Base de Conhecimento"
      >
        <form onSubmit={handleCreate} className="space-y-4">
          {formError && (
            <div className="p-3 rounded-lg bg-red-950/60 border border-red-800 text-red-300 text-xs">
              {formError}
            </div>
          )}

          <Input
            id="kbName"
            label="Nome da Base"
            required
            placeholder="ex: Documentação Financeira, Manuais RH"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />

          <Input
            id="kbDesc"
            label="Descrição"
            placeholder="Breve resumo sobre o conteúdo dos documentos desta base"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />

          <div className="space-y-1.5">
            <label htmlFor="kbVis" className="block text-xs font-medium text-slate-300">
              Visibilidade
            </label>
            <select
              id="kbVis"
              className="w-full bg-slate-900 border border-slate-700/80 rounded-lg px-3.5 py-2 text-sm text-slate-100 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-colors"
              value={visibility}
              onChange={(e) => setVisibility(e.target.value as any)}
            >
              <option value="private">Privada (Apenas eu)</option>
              <option value="shared">Compartilhada (Equipe autenticada)</option>
              <option value="public">Pública (Link externo)</option>
            </select>
          </div>

          <div className="space-y-1.5">
            <label htmlFor="kbEmbed" className="block text-xs font-medium text-slate-300">
              Modelo de Embeddings
            </label>
            <select
              id="kbEmbed"
              className="w-full bg-slate-900 border border-slate-700/80 rounded-lg px-3.5 py-2 text-sm text-slate-100 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-colors"
              value={embeddingModel}
              onChange={(e) => setEmbeddingModel(e.target.value)}
            >
              <option value="text-embedding-3-small">text-embedding-3-small (Recomendado)</option>
              <option value="text-embedding-3-large">text-embedding-3-large</option>
              <option value="text-embedding-ada-002">text-embedding-ada-002</option>
            </select>
          </div>

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
            <Button type="button" variant="ghost" onClick={() => setIsModalOpen(false)}>
              Cancelar
            </Button>
            <Button type="submit" variant="primary" isLoading={isSaving} className="bg-emerald-600 hover:bg-emerald-500">
              Criar Base
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
