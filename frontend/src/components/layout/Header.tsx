import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';
import { UserMenu } from './UserMenu';

export const Header: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/80 backdrop-blur-md px-6 flex items-center justify-between z-20">
      <div className="flex items-center gap-3">
        {/* Placeholder para titulo contextual ou breadcrumbs */}
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={toggleTheme}
          className="p-2 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800/80 border border-slate-800 transition-colors cursor-pointer"
          aria-label="Alternar Tema"
        >
          {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-indigo-400" />}
        </button>

        <div className="h-6 w-px bg-slate-800" />

        <UserMenu />
      </div>
    </header>
  );
};
