import React, { useState, useRef } from 'react';
import { Send, Square } from 'lucide-react';
import { Button } from '../ui/Button';

interface ChatInputProps {
  onSend: (message: string) => void;
  onStop?: () => void;
  isGenerating?: boolean;
  disabled?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSend,
  onStop,
  isGenerating,
  disabled,
}) => {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = () => {
    if (!text.trim() || isGenerating || disabled) return;
    onSend(text.trim());
    setText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 160)}px`;
  };

  return (
    <div className="p-4 bg-slate-900/90 border-t border-slate-800 backdrop-blur-md">
      <div className="max-w-4xl mx-auto flex items-end gap-3 bg-slate-950/80 border border-slate-800 rounded-2xl p-2.5 focus-within:border-indigo-500/80 focus-within:ring-1 focus-within:ring-indigo-500/80 transition-all">
        <textarea
          ref={textareaRef}
          rows={1}
          placeholder="Envie uma mensagem para o agente de IA... (Shift+Enter para nova linha)"
          value={text}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          className="flex-1 bg-transparent border-0 resize-none text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-0 max-h-40 py-2 px-2"
        />

        {isGenerating ? (
          <Button
            type="button"
            variant="danger"
            size="sm"
            onClick={onStop}
            className="rounded-xl h-10 px-3.5"
            aria-label="Interromper geração"
          >
            <Square className="w-4 h-4 fill-current mr-1" />
            Parar
          </Button>
        ) : (
          <Button
            type="button"
            variant="primary"
            size="sm"
            disabled={!text.trim() || disabled}
            onClick={handleSend}
            className="rounded-xl h-10 w-10 p-0 shrink-0"
            aria-label="Enviar mensagem"
          >
            <Send className="w-4 h-4" />
          </Button>
        )}
      </div>
    </div>
  );
};
