import React, { useState, useRef, useEffect } from 'react';
import { LogOut, User as UserIcon, Shield } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

export const UserMenu: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { user, logout } = useAuth();
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  if (!user) return null;

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-3 p-1.5 rounded-xl hover:bg-slate-800/80 transition-colors cursor-pointer border border-transparent hover:border-slate-700"
      >
        <div className="w-8 h-8 rounded-lg bg-indigo-600/30 border border-indigo-500/40 text-indigo-300 flex items-center justify-center font-bold text-xs uppercase">
          {user.full_name ? user.full_name.charAt(0) : 'U'}
        </div>
        <div className="hidden sm:block text-left">
          <p className="text-xs font-semibold text-slate-200 leading-tight">{user.full_name}</p>
          <p className="text-[11px] text-slate-400">{user.email}</p>
        </div>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 rounded-xl bg-slate-900 border border-slate-800 shadow-2xl p-1.5 z-50 animate-fade-in">
          <div className="px-3 py-2 border-b border-slate-800/80 mb-1">
            <p className="text-xs font-semibold text-white">{user.full_name}</p>
            <div className="flex items-center gap-1.5 mt-1">
              <Shield className="w-3 h-3 text-indigo-400" />
              <span className="text-[11px] text-indigo-300">
                {user.is_superuser ? 'Superusuário' : user.roles?.[0] || 'Usuário'}
              </span>
            </div>
          </div>

          <div className="space-y-0.5">
            <div className="flex items-center gap-2 px-3 py-2 text-xs text-slate-300 rounded-lg hover:bg-slate-800/60 cursor-pointer">
              <UserIcon className="w-4 h-4 text-slate-400" />
              <span>Meu Perfil</span>
            </div>

            <button
              onClick={() => {
                setIsOpen(false);
                logout();
              }}
              className="w-full flex items-center gap-2 px-3 py-2 text-xs text-red-400 hover:text-red-300 rounded-lg hover:bg-red-950/40 cursor-pointer transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span>Sair da Conta</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
