import { apiFetch } from './api';
import { User } from '../types/auth';
import { Role, Permission } from '../types/role';

export const adminService = {
  // Usuários
  async listUsers(): Promise<User[]> {
    return apiFetch<User[]>('/users');
  },

  async updateUserRoles(userId: string, roles: string[]): Promise<User> {
    return apiFetch<User>(`/users/${userId}/roles`, {
      method: 'PUT',
      body: JSON.stringify({ roles }),
    });
  },

  async toggleUserStatus(userId: string, isActive: boolean): Promise<User> {
    return apiFetch<User>(`/users/${userId}`, {
      method: 'PATCH',
      body: JSON.stringify({ is_active: isActive }),
    });
  },

  // Papéis & Permissões
  async listRoles(): Promise<Role[]> {
    return apiFetch<Role[]>('/roles');
  },

  async listPermissions(): Promise<Permission[]> {
    return apiFetch<Permission[]>('/roles/permissions');
  },

  async createRole(data: { name: string; description?: string; permission_ids: string[] }): Promise<Role> {
    return apiFetch<Role>('/roles', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async updateRole(roleId: string, data: { name: string; description?: string; permission_ids: string[] }): Promise<Role> {
    return apiFetch<Role>(`/roles/${roleId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async deleteRole(roleId: string): Promise<void> {
    return apiFetch(`/roles/${roleId}`, { method: 'DELETE' });
  },
};
