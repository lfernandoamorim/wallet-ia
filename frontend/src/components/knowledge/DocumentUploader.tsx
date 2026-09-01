import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertCircle } from 'lucide-react';
import { Button } from '../ui/Button';

interface DocumentUploaderProps {
  onUpload: (file: File) => Promise<void>;
  isLoading?: boolean;
}

export const DocumentUploader: React.FC<DocumentUploaderProps> = ({ onUpload, isLoading }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [statusMessage, setStatusMessage] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = (file: File) => {
    setSelectedFile(file);
    setUploadStatus('idle');
    setStatusMessage('');
  };

  const handleStartUpload = async () => {
    if (!selectedFile) return;
    try {
      await onUpload(selectedFile);
      setUploadStatus('success');
      setStatusMessage(`Arquivo "${selectedFile.name}" enviado com sucesso.`);
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err: unknown) {
      setUploadStatus('error');
      setStatusMessage(err instanceof Error ? err.message : 'Erro ao enviar documento');
    }
  };

  return (
    <div className="space-y-4">
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all ${
          dragActive
            ? 'border-indigo-500 bg-indigo-500/10 scale-[1.01]'
            : 'border-slate-800 bg-slate-900/40 hover:border-slate-700 hover:bg-slate-900/60'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".md,.docx,.xlsx,.txt,.pdf"
          onChange={handleChange}
        />

        <div className="w-12 h-12 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center mx-auto text-indigo-400 mb-3">
          <UploadCloud className="w-6 h-6" />
        </div>

        <p className="text-sm font-semibold text-slate-200">
          Arraste e solte o documento aqui ou <span className="text-indigo-400">clique para selecionar</span>
        </p>
        <p className="text-xs text-slate-500 mt-1">
          Formatos suportados: Markdown (.md), Word (.docx), Excel (.xlsx), PDF (.pdf), Texto (.txt)
        </p>
      </div>

      {selectedFile && (
        <div className="flex items-center justify-between p-3.5 bg-slate-900 border border-slate-800 rounded-xl animate-fade-in">
          <div className="flex items-center gap-3 truncate">
            <FileText className="w-5 h-5 text-indigo-400 shrink-0" />
            <div className="truncate">
              <p className="text-xs font-medium text-slate-200 truncate">{selectedFile.name}</p>
              <p className="text-[11px] text-slate-500">{(selectedFile.size / 1024).toFixed(1)} KB</p>
            </div>
          </div>
          <Button
            size="sm"
            variant="primary"
            isLoading={isLoading}
            onClick={handleStartUpload}
            className="shrink-0"
          >
            Indexar Documento
          </Button>
        </div>
      )}

      {uploadStatus !== 'idle' && (
        <div
          className={`flex items-center gap-2 p-3 rounded-lg text-xs font-medium ${
            uploadStatus === 'success'
              ? 'bg-emerald-950/60 border border-emerald-800/80 text-emerald-300'
              : 'bg-red-950/60 border border-red-800/80 text-red-300'
          }`}
        >
          {uploadStatus === 'success' ? (
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
          ) : (
            <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
          )}
          <span>{statusMessage}</span>
        </div>
      )}
    </div>
  );
};
