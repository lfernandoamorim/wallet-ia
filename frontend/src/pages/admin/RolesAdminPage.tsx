import React, { useEffect, useState } from 'react';
import { ShieldAlert, Plus, Edit2, Trash2, ShieldCheck } from 'lucide-react';
import { Role, Permission } from '../../types/role';
import { adminService } from '../../services/admin.service';
import { RoleEditorModal } from '../../components/admin/RoleEditorModal';
import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';

export const RolesAdminPage: React.FC = () => {
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [rolesData, permsData] = await Promise.all([
        adminService.listRoles(),
        adminService.listPermissions(),
      ]);
      setRoles(rolesData);
      setPermissions(permsData);
    } catch {
      setRoles([]);
      setPermissions([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSaveRole = async (data: { name: string; description?: string; permission_ids: string[] }) => {
    if (editingRole) {
      await adminService.updateRole(editingRole.id, data);
    } else {
      await adminService.createRole(data);
    }
    await loadData();
  };

  const handleDeleteRole = async (roleId: string) => {
    if (confirm('Tem certeza que deseja remover este papel? Usuários com este papel perderão as permissões associadas.')) {
      await adminService.deleteRole(roleId);
      await loadData();
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <ShieldAlert className="w-7 h-7 text-indigo-400" />
            Papéis & Matriz de Permissões (RBAC)
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Configure permissões granulares para cada perfil de acesso na plataforma.
          </p>
        </div>

        <Button
          onClick={() => {
            setEditingRole(null);
            setIsModalOpen(true);
          }}
          variant="primary"
          className="shadow-lg shadow-indigo-600/20"
        >
          <Plus className="w-4 h-4 mr-1.5" />
          Novo Papel
        </Button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin h-8 w-8 border-4 border-indigo-500 border-t-transparent rounded-full" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {roles.map((role) => (
            <Card key={role.id} className="flex flex-col justify-between space-y-4">
              <div>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                      <ShieldCheck className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-base font-semibold text-white">{role.name}</h3>
                      {role.is_system && (
                        <Badge variant="info" className="mt-1">Sistema</Badge>
                      )}
                    </div>
                  </div>

                  {!role.is_system && (
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => {
                          setEditingRole(role);
                          setIsModalOpen(true);
                        }}
                        className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors cursor-pointer"
                        aria-label="Editar Papel"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteRole(role.id)}
                        className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-red-950/40 rounded-lg transition-colors cursor-pointer"
                        aria-label="Excluir Papel"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  )}
                </div>

                <p className="mt-3 text-xs text-slate-400">
                  {role.description || 'Sem descrição informada.'}
                </p>

                <div className="mt-4 space-y-1.5">
                  <p className="text-[11px] font-semibold text-slate-400 uppercase">
                    Permissões Atribuídas ({role.permissions?.length || 0})
                  </p>
                  <div className="flex flex-wrap gap-1.5 max-h-32 overflow-y-auto p-1 bg-slate-950/40 rounded-lg border border-slate-800/60">
                    {role.permissions && role.permissions.length > 0 ? (
                      role.permissions.map((p) => (
                        <span
                          key={p.id}
                          className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300 border border-slate-700"
                        >
                          {p.name}
                        </span>
                      ))
                    ) : (
                      <span className="text-[11px] text-slate-500 italic p-1">Nenhuma permissão específica</span>
                    )}
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      <RoleEditorModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveRole}
        initialRole={editingRole}
        availablePermissions={permissions}
      />
    </div>
  );
};
