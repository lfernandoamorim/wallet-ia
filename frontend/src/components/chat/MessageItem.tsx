import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Bot, User, Sparkles } from 'lucide-react';
import { Message } from '../../types/conversation';
import { CodeBlock } from './CodeBlock';

interface MessageItemProps {
  message: Message;
  isStreaming?: boolean;
}

export const MessageItem: React.FC<MessageItemProps> = ({ message, isStreaming }) => {
  const isAgent = message.sender_type === 'agent' || message.sender_type === 'system';

  return (
    <div
      className={`flex gap-4 p-4 rounded-2xl transition-colors ${
        isAgent
          ? 'bg-slate-900/60 border border-slate-800/80 shadow-sm'
          : 'bg-indigo-950/20 border border-indigo-900/30'
      }`}
    >
      <div
        className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 ${
          isAgent
            ? 'bg-indigo-600/20 border border-indigo-500/30 text-indigo-400'
            : 'bg-violet-600/20 border border-violet-500/30 text-violet-400'
        }`}
      >
        {isAgent ? <Bot className="w-5 h-5" /> : <User className="w-5 h-5" />}
      </div>

      <div className="flex-1 min-w-0 space-y-1">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-300">
            {isAgent ? 'Assistente Wallet IA' : 'Você'}
          </span>
          <span className="text-[11px] text-slate-500">
            {message.created_at ? new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Agora'}
          </span>
        </div>

        <div className="prose prose-invert prose-sm max-w-none text-slate-200 leading-relaxed break-words">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code({ className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || '');
                const isInline = !match && !String(children).includes('\n');
                if (isInline) {
                  return (
                    <code className="bg-slate-800 text-indigo-300 px-1.5 py-0.5 rounded text-xs font-mono" {...props}>
                      {children}
                    </code>
                  );
                }
                return (
                  <CodeBlock
                    language={match ? match[1] : 'text'}
                    value={String(children).replace(/\n$/, '')}
                  />
                );
              },
            }}
          >
            {message.content}
          </ReactMarkdown>

          {isStreaming && (
            <span className="inline-flex items-center gap-1 text-indigo-400 font-bold ml-1 animate-pulse">
              <Sparkles className="w-3.5 h-3.5" />
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
