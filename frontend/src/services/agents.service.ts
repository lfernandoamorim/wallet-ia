import { apiFetch } from './api';
import { Agent } from '../types/agent';

export const agentsService = {
  async list(): Promise<Agent[]> {
    return apiFetch<Agent[]>('/agents');
  },

  async getById(id: string): Promise<Agent> {
    return apiFetch<Agent>(`/agents/${id}`);
  },

  async create(data: Partial<Agent>): Promise<Agent> {
    return apiFetch<Agent>('/agents', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async update(id: string, data: Partial<Agent>): Promise<Agent> {
    return apiFetch<Agent>(`/agents/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  async delete(id: string): Promise<void> {
    return apiFetch(`/agents/${id}`, { method: 'DELETE' });
  },
};
