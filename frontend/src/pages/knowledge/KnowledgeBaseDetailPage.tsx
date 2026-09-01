import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, BookOpen, Trash2, FileText, CheckCircle2, Clock, AlertTriangle } from 'lucide-react';
import { KnowledgeBase, KBDocument } from '../../types/knowledge';
import { kbService } from '../../services/kb.service';
import { DocumentUploader } from '../../components/knowledge/DocumentUploader';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';

export const KnowledgeBaseDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [kb, setKb] = useState<KnowledgeBase | null>(null);
  const [documents, setDocuments] = useState<KBDocument[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);

  const loadData = async () => {
    if (!id) return;
    setIsLoading(true);
    try {
      const [kbData, docsData] = await Promise.all([
        kbService.getById(id),
        kbService.listDocuments(id),
      ]);
      setKb(kbData);
      setDocuments(docsData);
    } catch {
      navigate('/knowledge');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [id]);

  const handleUpload = async (file: File) => {
    if (!id) return;
    setIsUploading(true);
    try {
      await kbService.uploadDocument(id, file);
      await loadData();
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteDocument = async (docId: string) => {
    if (!id) return;
    if (confirm('Tem certeza que deseja remover este documento e seus chunks vetoriais?')) {
      await kbService.deleteDocument(id, docId);
      await loadData();
    }
  };

  const statusIcons = {
    indexed: <CheckCircle2 className="w-4 h-4 text-emerald-400" />,
    processing: <Clock className="w-4 h-4 text-amber-400 animate-spin" />,
    failed: <AlertTriangle className="w-4 h-4 text-red-400" />,
  };

  const statusBadges = {
    indexed: <Badge variant="success">Indexado</Badge>,
    processing: <Badge variant="warning">Processando</Badge>,
    failed: <Badge variant="danger">Falhou</Badge>,
  };

  if (isLoading || !kb) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="animate-spin h-8 w-8 border-4 border-emerald-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => navigate('/knowledge')}
        className="text-slate-400 hover:text-slate-200 -ml-2"
      >
        <ArrowLeft className="w-4 h-4 mr-1.5" />
        Voltar para Bases de Conhecimento
      </Button>

      {/* Header card */}
      <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-emerald-600/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <BookOpen className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">{kb.name}</h1>
              <p className="text-xs text-slate-400">{kb.description || 'Sem descrição.'}</p>
            </div>
          </div>
          <Badge variant="info">{kb.embedding_model}</Badge>
        </div>
      </div>

      {/* Uploader */}
      <div className="space-y-2">
        <h2 className="text-base font-semibold text-slate-200">Carregar Novos Documentos</h2>
        <DocumentUploader onUpload={handleUpload} isLoading={isUploading} />
      </div>

      {/* Documents List */}
      <div className="space-y-3 pt-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-slate-200">
            Documentos Indexados ({documents.length})
          </h2>
        </div>

        {documents.length === 0 ? (
          <div className="text-center py-12 border border-slate-800 rounded-xl bg-slate-900/30">
            <FileText className="w-8 h-8 text-slate-600 mx-auto mb-2" />
            <p className="text-xs text-slate-400">Nenhum documento adicionado a esta base ainda.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="flex items-center justify-between p-4 bg-slate-900/80 border border-slate-800/80 rounded-xl hover:border-slate-700 transition-colors"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="p-2 rounded-lg bg-slate-800 text-slate-300">
                    <FileText className="w-5 h-5" />
                  </div>
                  <div className="truncate">
                    <h4 className="text-sm font-medium text-slate-200 truncate">{doc.file_name}</h4>
                    <div className="flex items-center gap-3 text-[11px] text-slate-500 mt-0.5">
                      <span>{(doc.file_size / 1024).toFixed(1)} KB</span>
                      <span>•</span>
                      <span>{doc.chunk_count} chunk(s) gerados</span>
                      <span>•</span>
                      <span>{new Date(doc.created_at).toLocaleDateString('pt-BR')}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4 shrink-0">
                  <div className="flex items-center gap-1.5">
                    {statusIcons[doc.status]}
                    {statusBadges[doc.status]}
                  </div>

                  <button
                    onClick={() => handleDeleteDocument(doc.id)}
                    className="p-1.5 text-slate-500 hover:text-red-400 hover:bg-red-950/40 rounded-lg transition-colors cursor-pointer"
                    aria-label="Remover documento"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
