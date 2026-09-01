import { apiFetch } from './api';
import { Conversation, Message } from '../types/conversation';

export const chatService = {
  async listConversations(): Promise<Conversation[]> {
    return apiFetch<Conversation[]>('/conversations');
  },

  async getConversation(id: string): Promise<Conversation> {
    return apiFetch<Conversation>(`/conversations/${id}`);
  },

  async createConversation(agentId: string, title?: string): Promise<Conversation> {
    return apiFetch<Conversation>('/conversations', {
      method: 'POST',
      body: JSON.stringify({ agent_id: agentId, title: title || 'Nova Conversa' }),
    });
  },

  async deleteConversation(id: string): Promise<void> {
    return apiFetch(`/conversations/${id}`, { method: 'DELETE' });
  },

  async listMessages(conversationId: string): Promise<Message[]> {
    return apiFetch<Message[]>(`/conversations/${conversationId}/messages`);
  },

  async sendMessage(conversationId: string, content: string): Promise<Message> {
    return apiFetch<Message>(`/conversations/${conversationId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ content }),
    });
  },
};
