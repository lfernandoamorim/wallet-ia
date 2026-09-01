import React, { useEffect, useState } from 'react';
import { Users, Search, Shield, CheckCircle, XCircle } from 'lucide-react';
import { User } from '../../types/auth';
import { Role } from '../../types/role';
import { adminService } from '../../services/admin.service';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';

export const UsersAdminPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [search, setSearch] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [usersData, rolesData] = await Promise.all([
        adminService.listUsers(),
        adminService.listRoles(),
      ]);
      setUsers(usersData);
      setRoles(rolesData);
    } catch {
      setUsers([]);
      setRoles([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleToggleActive = async (user: User) => {
    try {
      await adminService.toggleUserStatus(user.id, !user.is_active);
      await loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleRoleChange = async (userId: string, selectedRole: string) => {
    try {
      await adminService.updateUserRoles(userId, [selectedRole]);
      await loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const filteredUsers = users.filter(
    (u) =>
      u.full_name?.toLowerCase().includes(search.toLowerCase()) ||
      u.email.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <Users className="w-7 h-7 text-indigo-400" />
          Gestão de Usuários
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Controle de contas, atribuição de papéis e ativação/desativação de acesso.
        </p>
      </div>

      <div className="relative">
        <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          placeholder="Buscar usuários por nome ou e-mail..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
        />
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin h-8 w-8 border-4 border-indigo-500 border-t-transparent rounded-full" />
        </div>
      ) : (
        <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-900/60 shadow-xl">
          <table className="w-full text-left text-sm text-slate-200">
            <thead className="bg-slate-950/80 text-xs font-semibold text-slate-400 uppercase border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">Usuário</th>
                <th className="px-6 py-4">Papel (Role)</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Criado em</th>
                <th className="px-6 py-4 text-right">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-xs">
              {filteredUsers.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-slate-500">
                    Nenhum usuário encontrado.
                  </td>
                </tr>
              ) : (
                filteredUsers.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30 text-indigo-400 flex items-center justify-center font-bold text-xs uppercase">
                          {u.full_name ? u.full_name.charAt(0) : 'U'}
                        </div>
                        <div>
                          <p className="font-semibold text-slate-100">{u.full_name}</p>
                          <p className="text-slate-500">{u.email}</p>
                        </div>
                      </div>
                    </td>

                    <td className="px-6 py-4">
                      {u.is_superuser ? (
                        <Badge variant="danger" className="flex items-center gap-1 w-fit">
                          <Shield className="w-3 h-3" />
                          Superusuário
                        </Badge>
                      ) : (
                        <select
                          value={u.roles?.[0] || ''}
                          onChange={(e) => handleRoleChange(u.id, e.target.value)}
                          className="bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 cursor-pointer"
                        >
                          <option value="" disabled>Selecionar papel...</option>
                          {roles.map((r) => (
                            <option key={r.id} value={r.name}>
                              {r.name}
                            </option>
                          ))}
                        </select>
                      )}
                    </td>

                    <td className="px-6 py-4">
                      {u.is_active ? (
                        <Badge variant="success" className="flex items-center gap-1 w-fit">
                          <CheckCircle className="w-3 h-3" />
                          Ativo
                        </Badge>
                      ) : (
                        <Badge variant="default" className="flex items-center gap-1 w-fit">
                          <XCircle className="w-3 h-3" />
                          Inativo
                        </Badge>
                      )}
                    </td>

                    <td className="px-6 py-4 text-slate-400">
                      {new Date(u.created_at || Date.now()).toLocaleDateString('pt-BR')}
                    </td>

                    <td className="px-6 py-4 text-right">
                      {!u.is_superuser && (
                        <Button
                          size="sm"
                          variant={u.is_active ? 'danger' : 'outline'}
                          onClick={() => handleToggleActive(u)}
                          className="text-xs"
                        >
                          {u.is_active ? 'Desativar' : 'Ativar'}
                        </Button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
