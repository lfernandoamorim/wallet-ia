import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Bot, 
  MessageSquare, 
  BookOpen, 
  KeyRound, 
  Users, 
  ShieldAlert, 
  ChevronLeft, 
  ChevronRight,
  Sparkles 
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

export const Sidebar: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const { hasPermission } = useAuth();

  const navItems = [
    { label: 'Chat', path: '/chat', icon: MessageSquare },
    { label: 'Agentes', path: '/agents', icon: Bot },
    { label: 'Base de Conhecimento', path: '/knowledge', icon: BookOpen },
    { label: 'Provedores de IA', path: '/providers', icon: KeyRound },
  ];

  const adminItems = [
    { label: 'Usuários', path: '/admin/users', icon: Users, permission: 'users:read' },
    { label: 'Papéis & Permissões', path: '/admin/roles', icon: ShieldAlert, permission: 'roles:read' },
  ];

  return (
    <aside
      className={`relative flex flex-col border-r border-slate-800 bg-slate-900/95 transition-all duration-300 z-30 ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      <div className="flex items-center justify-between p-4 border-b border-slate-800 h-16">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-gradient-to-tr from-indigo-600 to-violet-500 text-white shadow-md">
              <Sparkles className="w-5 h-5" />
            </div>
            <span className="font-bold text-lg bg-gradient-to-r from-indigo-300 to-violet-300 bg-clip-text text-transparent">
              Wallet IA
            </span>
          </div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors mx-auto cursor-pointer"
          aria-label={collapsed ? 'Expandir menu lateral' : 'Recolher menu lateral'}
        >
          {collapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
        </button>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1.5 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`
            }
          >
            <item.icon className="w-5 h-5 shrink-0" />
            {!collapsed && <span>{item.label}</span>}
          </NavLink>
        ))}

        <div className="pt-4 border-t border-slate-800/80 my-2">
          {!collapsed && <p className="px-3 text-xs font-semibold uppercase text-slate-400 mb-2">Administração</p>}
          {adminItems.map((item) => {
            if (item.permission && !hasPermission(item.permission)) return null;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`
                }
              >
                <item.icon className="w-5 h-5 shrink-0" />
                {!collapsed && <span>{item.label}</span>}
              </NavLink>
            );
          })}
        </div>
      </nav>
    </aside>
  );
};
