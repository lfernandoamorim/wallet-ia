import React, { useState, useEffect } from 'react';
import { Role, Permission } from '../../types/role';
import { Modal } from '../ui/Modal';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';

interface RoleEditorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: { name: string; description?: string; permission_ids: string[] }) => Promise<void>;
  initialRole?: Role | null;
  availablePermissions: Permission[];
}

export const RoleEditorModal: React.FC<RoleEditorModalProps> = ({
  isOpen,
  onClose,
  onSave,
  initialRole,
  availablePermissions,
}) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [selectedPermissionIds, setSelectedPermissionIds] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialRole) {
      setName(initialRole.name || '');
      setDescription(initialRole.description || '');
      setSelectedPermissionIds(initialRole.permissions ? initialRole.permissions.map((p) => p.id) : []);
    } else {
      setName('');
      setDescription('');
      setSelectedPermissionIds([]);
    }
    setError(null);
  }, [initialRole, isOpen]);

  const togglePermission = (permId: string) => {
    setSelectedPermissionIds((prev) =>
      prev.includes(permId) ? prev.filter((id) => id !== permId) : [...prev, permId]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await onSave({
        name,
        description,
        permission_ids: selectedPermissionIds,
      });
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Falha ao salvar papel');
    } finally {
      setIsLoading(false);
    }
  };

  // Agrupar permissoes por categoria
  const groupedPerms = availablePermissions.reduce<Record<string, Permission[]>>((acc, perm) => {
    const cat = perm.category || 'Geral';
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(perm);
    return acc;
  }, {});

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={initialRole ? 'Editar Papel (Role)' : 'Novo Papel (Role)'}
      maxWidth="max-w-2xl"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 rounded-lg bg-red-950/60 border border-red-800 text-red-300 text-xs">
            {error}
          </div>
        )}

        <Input
          id="roleName"
          label="Nome do Papel"
          required
          placeholder="ex: Analista, Gerente, Suporte"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />

        <Input
          id="roleDesc"
          label="Descrição"
          placeholder="Finalidade e escopo de acesso deste papel"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />

        <div className="space-y-2 pt-2">
          <label className="block text-xs font-semibold text-slate-200">
            Matriz de Permissões ({selectedPermissionIds.length} selecionadas)
          </label>

          <div className="max-h-60 overflow-y-auto space-y-4 p-3 bg-slate-950/60 border border-slate-800 rounded-xl">
            {Object.entries(groupedPerms).map(([category, perms]) => (
              <div key={category} className="space-y-2">
                <p className="text-[11px] font-bold text-indigo-400 uppercase tracking-wider">{category}</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {perms.map((p) => {
                    const isChecked = selectedPermissionIds.includes(p.id);
                    return (
                      <label
                        key={p.id}
                        className={`flex items-center gap-2 p-2 rounded-lg border text-xs cursor-pointer transition-colors ${
                          isChecked
                            ? 'bg-indigo-950/40 border-indigo-700/60 text-slate-100'
                            : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-700'
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => togglePermission(p.id)}
                          className="rounded border-slate-700 text-indigo-600 focus:ring-0 cursor-pointer"
                        />
                        <div>
                          <p className="font-medium leading-none">{p.name}</p>
                          {p.description && (
                            <p className="text-[10px] text-slate-500 mt-0.5">{p.description}</p>
                          )}
                        </div>
                      </label>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" variant="primary" isLoading={isLoading}>
            {initialRole ? 'Salvar Papel' : 'Criar Papel'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};
