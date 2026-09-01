import React, { useEffect } from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react';

export interface ToastProps {
  id: string;
  message: string;
  type?: 'success' | 'error' | 'info';
  duration?: number;
  onClose: (id: string) => void;
}

export const Toast: React.FC<ToastProps> = ({
  id,
  message,
  type = 'info',
  duration = 4000,
  onClose,
}) => {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose(id);
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [id, duration, onClose]);

  const icons = {
    success: <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />,
    error: <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />,
    info: <Info className="w-5 h-5 text-indigo-400 shrink-0" />,
  };

  const borderColors = {
    success: 'border-emerald-800/80 bg-slate-900/95',
    error: 'border-red-800/80 bg-slate-900/95',
    info: 'border-indigo-800/80 bg-slate-900/95',
  };

  return (
    <div
      className={twMerge(
        clsx(
          'flex items-center gap-3 px-4 py-3 rounded-xl border shadow-lg text-sm text-slate-100 backdrop-blur-md transition-all',
          borderColors[type]
        )
      )}
    >
      {icons[type]}
      <span className="flex-1 font-medium">{message}</span>
      <button
        onClick={() => onClose(id)}
        className="text-slate-400 hover:text-slate-200 p-0.5 rounded transition-colors cursor-pointer"
        aria-label="Fechar notificação"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
};
