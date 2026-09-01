import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Plus, Trash2, Bot, MessageSquare } from 'lucide-react';
import { Conversation, Message } from '../../types/conversation';
import { Agent } from '../../types/agent';
import { chatService } from '../../services/chat.service';
import { agentsService } from '../../services/agents.service';
import { useChatStream } from '../../hooks/useChatStream';
import { MessageList } from '../../components/chat/MessageList';
import { ChatInput } from '../../components/chat/ChatInput';
import { Button } from '../../components/ui/Button';

export const ChatPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const agentQueryParam = searchParams.get('agent');

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversation, setActiveConversation] = useState<Conversation | null>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgentId, setSelectedAgentId] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const { isGenerating, streamedContent, startStream, stopStream } = useChatStream({
    onComplete: async () => {
      if (activeConversation) {
        const updatedMsgs = await chatService.listMessages(activeConversation.id);
        setMessages(updatedMsgs);
      }
    },
  });

  const loadInitialData = async () => {
    setIsLoading(true);
    try {
      const [convsData, agentsData] = await Promise.all([
        chatService.listConversations(),
        agentsService.list(),
      ]);

      setConversations(convsData);
      setAgents(agentsData);

      const targetAgentId = agentQueryParam || (agentsData[0]?.id ?? '');
      setSelectedAgentId(targetAgentId);

      if (convsData.length > 0) {
        setActiveConversation(convsData[0]);
        const msgs = await chatService.listMessages(convsData[0].id);
        setMessages(msgs);
      }
    } catch {
      setConversations([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  const handleSelectConversation = async (conv: Conversation) => {
    setActiveConversation(conv);
    setSelectedAgentId(conv.agent_id);
    const msgs = await chatService.listMessages(conv.id);
    setMessages(msgs);
  };

  const handleNewChat = async () => {
    if (!selectedAgentId && agents.length === 0) return;
    const agentId = selectedAgentId || agents[0].id;
    try {
      const newConv = await chatService.createConversation(agentId, 'Nova Conversa');
      setConversations((prev) => [newConv, ...prev]);
      setActiveConversation(newConv);
      setMessages([]);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteConversation = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Tem certeza que deseja excluir esta conversa?')) {
      await chatService.deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (activeConversation?.id === id) {
        setActiveConversation(null);
        setMessages([]);
      }
    }
  };

  const handleSendMessage = async (text: string) => {
    let conv = activeConversation;
    if (!conv) {
      if (!selectedAgentId && agents.length === 0) return;
      conv = await chatService.createConversation(selectedAgentId || agents[0].id, text.slice(0, 30));
      setConversations((prev) => [conv!, ...prev]);
      setActiveConversation(conv);
    }

    // Otimista
    const optimisticUserMsg: Message = {
      id: `temp-${Date.now()}`,
      conversation_id: conv.id,
      sender_type: 'user',
      content: text,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, optimisticUserMsg]);

    await startStream(conv.id, text);
  };

  return (
    <div className="flex h-[calc(100vh-6.5rem)] rounded-2xl overflow-hidden border border-slate-800 bg-slate-900/50 backdrop-blur-xl">
      {/* Sidebar de Histórico de Conversas */}
      <div className="w-80 border-r border-slate-800 bg-slate-900/80 flex flex-col justify-between shrink-0">
        <div className="p-4 border-b border-slate-800 space-y-3">
          <Button
            onClick={handleNewChat}
            variant="primary"
            className="w-full justify-center shadow-md shadow-indigo-600/20"
          >
            <Plus className="w-4 h-4 mr-1.5" />
            Novo Chat
          </Button>

          {agents.length > 0 && (
            <div className="space-y-1">
              <label className="text-[11px] font-semibold text-slate-400 uppercase">
                Agente Selecionado
              </label>
              <select
                value={selectedAgentId}
                onChange={(e) => setSelectedAgentId(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                {agents.map((agent) => (
                  <option key={agent.id} value={agent.id}>
                    {agent.name} ({agent.provider})
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Lista de Conversas */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {conversations.length === 0 ? (
            <div className="text-center py-8 text-xs text-slate-500">
              Nenhuma conversa recente.
            </div>
          ) : (
            conversations.map((conv) => (
              <div
                key={conv.id}
                onClick={() => handleSelectConversation(conv)}
                className={`flex items-center justify-between p-2.5 rounded-xl cursor-pointer text-xs transition-colors group ${
                  activeConversation?.id === conv.id
                    ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 font-medium'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                <div className="flex items-center gap-2 truncate">
                  <MessageSquare className="w-3.5 h-3.5 shrink-0" />
                  <span className="truncate">{conv.title || 'Conversa sem título'}</span>
                </div>

                <button
                  onClick={(e) => handleDeleteConversation(conv.id, e)}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-400 transition-opacity"
                  aria-label="Excluir conversa"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Área Central de Mensagens e Input */}
      <div className="flex-1 flex flex-col min-w-0 bg-slate-950/60">
        {isLoading ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="animate-spin h-8 w-8 border-4 border-indigo-500 border-t-transparent rounded-full" />
          </div>
        ) : !activeConversation && messages.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
            <div className="w-14 h-14 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 mb-4 shadow-xl shadow-indigo-600/10">
              <Bot className="w-7 h-7" />
            </div>
            <h2 className="text-lg font-bold text-slate-100">Bem-vindo ao Chat da Wallet IA</h2>
            <p className="text-xs text-slate-400 mt-1.5 max-w-md">
              Envie uma pergunta para iniciar uma conversa com o agente selecionado com suporte a RAG e respostas inteligentes em tempo real.
            </p>
          </div>
        ) : (
          <MessageList
            messages={messages}
            streamingMessage={streamedContent}
            isStreaming={isGenerating}
          />
        )}

        <ChatInput
          onSend={handleSendMessage}
          onStop={stopStream}
          isGenerating={isGenerating}
        />
      </div>
    </div>
  );
};
