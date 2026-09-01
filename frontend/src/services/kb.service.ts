import { apiFetch } from './api';
import { KnowledgeBase, KBDocument } from '../types/knowledge';

export const kbService = {
  async list(): Promise<KnowledgeBase[]> {
    return apiFetch<KnowledgeBase[]>('/knowledge-bases');
  },

  async getById(id: string): Promise<KnowledgeBase> {
    return apiFetch<KnowledgeBase>(`/knowledge-bases/${id}`);
  },

  async create(data: Partial<KnowledgeBase>): Promise<KnowledgeBase> {
    return apiFetch<KnowledgeBase>('/knowledge-bases', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async delete(id: string): Promise<void> {
    return apiFetch(`/knowledge-bases/${id}`, { method: 'DELETE' });
  },

  async listDocuments(kbId: string): Promise<KBDocument[]> {
    return apiFetch<KBDocument[]>(`/knowledge-bases/${kbId}/documents`);
  },

  async uploadDocument(kbId: string, file: File): Promise<KBDocument> {
    const formData = new FormData();
    formData.append('file', file);
    return apiFetch<KBDocument>(`/knowledge-bases/${kbId}/documents`, {
      method: 'POST',
      body: formData,
    });
  },

  async deleteDocument(kbId: string, docId: string): Promise<void> {
    return apiFetch(`/knowledge-bases/${kbId}/documents/${docId}`, { method: 'DELETE' });
  },
};
