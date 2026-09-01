# Plano de Implementação — Frontend React da Plataforma Wallet IA

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir o frontend completo (SPA) da Plataforma Wallet IA em React, TypeScript, Vite e Tailwind CSS, integrado com a API FastAPI, streaming de chat, RAG e RBAC.

**Architecture:** Frontend modular em `frontend/` com separação por camadas (`components/`, `contexts/`, `hooks/`, `pages/`, `services/`, `types/`), consumo de API via cliente HTTP com interceptores JWT e streaming de IA em tempo real.

**Tech Stack:** React 19, TypeScript, Vite, Tailwind CSS, Lucide React, React Router DOM, Vitest, React Testing Library.

**Spec:** [`docs/superpowers/specs/2026-09-01-frontend-react-design.md`](file:///d:/Projetos/AdvanceSistemas/wallet-ia/docs/superpowers/specs/2026-09-01-frontend-react-design.md)

## Global Constraints

- Todo o código do frontend deve residir em `frontend/`.
- Tipagem estática rigorosa em TypeScript (`strict: true`).
- Tema Dark padrão com suporte completo a alternância Dark/Light.
- Nenhuma dependência não documentada; testes executados via `npm run test` / `npx vitest`.
- Mensagens e interfaces da UI em Português do Brasil (pt-BR).

---

### Task 1: Scaffolding e Configuração Base do Projeto Frontend

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tsconfig.node.json`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/postcss.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/index.css`
- Create: `frontend/src/App.tsx`
- Test: `frontend/src/App.test.tsx`

**Interfaces:**
- Produces: Estrutura inicial executável e ambiente de testes configurado com Vitest.

- [ ] **Step 1: Criar arquivos de configuração do Vite, TypeScript, Tailwind e Vitest**

Criar `frontend/package.json`:
```json
{
  "name": "wallet-ia-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "dependencies": {
    "clsx": "^2.1.1",
    "lucide-react": "^0.395.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-markdown": "^9.0.1",
    "react-router-dom": "^6.23.1",
    "remark-gfm": "^4.0.0",
    "tailwind-merge": "^2.3.0"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.4.5",
    "@testing-library/react": "^15.0.7",
    "@types/node": "^20.14.2",
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.0",
    "autoprefixer": "^10.4.19",
    "jsdom": "^24.1.0",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.4",
    "typescript": "^5.4.5",
    "vite": "^5.2.13",
    "vitest": "^1.6.0"
  }
}
```

Criar `frontend/vite.config.ts`:
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    host: true,
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
  },
});
```

Criar `frontend/src/test/setup.ts`:
```typescript
import '@testing-library/jest-dom';
```

Criar `frontend/tailwind.config.js`:
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eef2ff',
          100: '#e0e7ff',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
        },
      },
    },
  },
  plugins: [],
};
```

Criar `frontend/src/index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-slate-950 text-slate-100 antialiased selection:bg-indigo-500 selection:text-white;
    font-feature-settings: "cv02", "cv03", "cv04", "cv11";
  }
}
```

- [ ] **Step 2: Criar teste falho inicial `frontend/src/App.test.tsx`**

```tsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from './App';

describe('App Root', () => {
  it('renderiza o título da aplicação Wallet IA', () => {
    render(<App />);
    expect(screen.getByText(/Wallet IA/i)).toBeInTheDocument();
  });
});
```

- [ ] **Step 3: Implementar `frontend/src/App.tsx` e `frontend/src/main.tsx`**

`frontend/src/App.tsx`:
```tsx
import React from 'react';

export default function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center">
      <h1 className="text-3xl font-bold text-indigo-400">Wallet IA — Plataforma de IA</h1>
    </div>
  );
}
```

`frontend/src/main.tsx`:
```tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

- [ ] **Step 4: Instalar dependências e rodar teste**

Executar no terminal em `frontend/`:
```bash
npm install
npm test
```
Verificar que os testes passam e o build compila com `npm run build`.

- [ ] **Step 5: Commit**
```bash
git add frontend/
git commit -m "feat(frontend): setup inicial com Vite, React, Tailwind e Vitest"
```

---

### Task 2: Definições de Tipos TypeScript e Cliente HTTP Centralizado

**Files:**
- Create: `frontend/src/types/auth.ts`
- Create: `frontend/src/types/agent.ts`
- Create: `frontend/src/types/conversation.ts`
- Create: `frontend/src/types/knowledge.ts`
- Create: `frontend/src/types/provider.ts`
- Create: `frontend/src/types/role.ts`
- Create: `frontend/src/services/api.ts`
- Test: `frontend/src/services/api.test.ts`

**Interfaces:**
- Produces: Tipos TypeScript e método `apiFetch` com autenticação JWT e interceptors.

- [ ] **Step 1: Criar interfaces TypeScript em `frontend/src/types/`**

`frontend/src/types/auth.ts`:
```typescript
export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  roles: string[];
  permissions: string[];
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}
```

`frontend/src/types/agent.ts`:
```typescript
export interface Agent {
  id: string;
  name: string;
  description?: string;
  avatar_url?: string;
  system_prompt: string;
  provider: 'openrouter' | 'openai' | 'anthropic' | 'gemini';
  model_name: string;
  temperature: number;
  max_tokens?: number;
  visibility: 'private' | 'shared' | 'public';
  public_slug?: string;
  knowledge_base_ids: string[];
  created_at: string;
}
```

`frontend/src/types/conversation.ts`:
```typescript
export interface Attachment {
  id: string;
  file_name: string;
  file_size: number;
  file_type: string;
  file_url: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  sender_type: 'user' | 'agent' | 'system';
  content: string;
  attachments?: Attachment[];
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  agent_id: string;
  owner_id: string;
  visibility: 'private' | 'shared' | 'public';
  public_slug?: string;
  created_at: string;
  updated_at: string;
}
```

`frontend/src/types/knowledge.ts`:
```typescript
export interface KBDocument {
  id: string;
  knowledge_base_id: string;
  file_name: string;
  file_size: number;
  file_type: string;
  chunk_count: number;
  status: 'processing' | 'indexed' | 'failed';
  error_message?: string;
  created_at: string;
}

export interface KnowledgeBase {
  id: string;
  name: string;
  description?: string;
  visibility: 'private' | 'shared' | 'public';
  public_slug?: string;
  embedding_model: string;
  document_count?: number;
  created_at: string;
}
```

`frontend/src/types/provider.ts`:
```typescript
export interface ProviderCredential {
  id: string;
  provider: 'openrouter' | 'openai' | 'anthropic' | 'gemini';
  is_active: boolean;
  is_global: boolean;
  created_at: string;
}
```

`frontend/src/types/role.ts`:
```typescript
export interface Permission {
  id: string;
  name: string;
  description?: string;
  category: string;
}

export interface Role {
  id: string;
  name: string;
  description?: string;
  is_system: boolean;
  permissions: Permission[];
}
```

- [ ] **Step 2: Criar teste para o cliente HTTP em `frontend/src/services/api.test.ts`**

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiFetch, setAuthTokens, clearAuthTokens, getAccessToken } from './api';

describe('API Client', () => {
  beforeEach(() => {
    clearAuthTokens();
    vi.restoreAllMocks();
  });

  it('adiciona o header Authorization quando o token está definido', async () => {
    setAuthTokens('fake_access_token', 'fake_refresh_token');
    expect(getAccessToken()).toBe('fake_access_token');

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ status: 'ok' }),
    });
    global.fetch = mockFetch;

    await apiFetch('/test');

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/test'),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer fake_access_token',
        }),
      })
    );
  });
});
```

- [ ] **Step 3: Implementar `frontend/src/services/api.ts`**

```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

let accessToken: string | null = localStorage.getItem('wallet_ia_access_token');
let refreshToken: string | null = localStorage.getItem('wallet_ia_refresh_token');

export function setAuthTokens(access: string, refresh: string) {
  accessToken = access;
  refreshToken = refresh;
  localStorage.setItem('wallet_ia_access_token', access);
  localStorage.setItem('wallet_ia_refresh_token', refresh);
}

export function clearAuthTokens() {
  accessToken = null;
  refreshToken = null;
  localStorage.removeItem('wallet_ia_access_token');
  localStorage.removeItem('wallet_ia_refresh_token');
}

export function getAccessToken(): string | null {
  return accessToken;
}

export async function apiFetch<T = any>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;
  const headers = new Headers(options.headers || {});

  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  if (accessToken) {
    headers.set('Authorization', `Bearer ${accessToken}`);
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (response.status === 401 && refreshToken) {
    // Tenta renovar o token
    try {
      const refreshRes = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (refreshRes.ok) {
        const data = await refreshRes.json();
        setAuthTokens(data.access_token, data.refresh_token || refreshToken);
        headers.set('Authorization', `Bearer ${data.access_token}`);
        const retryRes = await fetch(url, { ...options, headers });
        if (!retryRes.ok) throw new Error(await retryRes.text());
        return await retryRes.json();
      }
    } catch {
      clearAuthTokens();
      window.location.href = '/login';
    }
  }

  if (!response.ok) {
    const errorBody = await response.text();
    let errorMessage = `Erro HTTP ${response.status}`;
    try {
      const parsed = JSON.parse(errorBody);
      errorMessage = parsed.detail || errorMessage;
    } catch {}
    throw new Error(errorMessage);
  }

  if (response.status === 204) return {} as T;
  return await response.json();
}
```

- [ ] **Step 4: Executar testes**
```bash
npm test
```

- [ ] **Step 5: Commit**
```bash
git add frontend/src/types/ frontend/src/services/
git commit -m "feat(frontend): adicionar tipos e cliente api com interceptor jwt"
```

---

### Task 3: Design System, Contexto de Tema e Componentes Primitivos de UI

**Files:**
- Create: `frontend/src/contexts/ThemeContext.tsx`
- Create: `frontend/src/components/ui/Button.tsx`
- Create: `frontend/src/components/ui/Input.tsx`
- Create: `frontend/src/components/ui/Modal.tsx`
- Create: `frontend/src/components/ui/Badge.tsx`
- Create: `frontend/src/components/ui/Card.tsx`
- Create: `frontend/src/components/ui/Toast.tsx`
- Test: `frontend/src/components/ui/Button.test.tsx`
- Test: `frontend/src/contexts/ThemeContext.test.tsx`

**Interfaces:**
- Produces: `ThemeContext` com alternância dark/light e componentes visuais primitivos.

- [ ] **Step 1: Criar testes para `ThemeContext` e `Button`**

`frontend/src/components/ui/Button.test.tsx`:
```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Button } from './Button';

describe('Button Component', () => {
  it('renderiza o botão com estilo primário e dispara evento onClick', () => {
    const handleClick = vi.fn();
    render(<Button variant="primary" onClick={handleClick}>Enviar</Button>);
    const btn = screen.getByRole('button', { name: /enviar/i });
    expect(btn).toBeInTheDocument();
    fireEvent.click(btn);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

- [ ] **Step 2: Implementar `frontend/src/contexts/ThemeContext.tsx`**

```tsx
import React, { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'dark' | 'light';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<Theme>(() => {
    const saved = localStorage.getItem('wallet_ia_theme') as Theme;
    return saved || 'dark';
  });

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    localStorage.setItem('wallet_ia_theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme deve ser usado dentro de ThemeProvider');
  return context;
};
```

- [ ] **Step 3: Implementar componentes de UI (`Button`, `Input`, `Modal`, `Badge`, `Card`, `Toast`)**

`frontend/src/components/ui/Button.tsx`:
```tsx
import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  isLoading,
  className,
  children,
  disabled,
  ...props
}) => {
  const base = 'inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none';
  
  const variants = {
    primary: 'bg-indigo-600 hover:bg-indigo-500 text-white focus:ring-indigo-500 shadow-sm',
    secondary: 'bg-slate-800 hover:bg-slate-700 text-slate-100 focus:ring-slate-600 border border-slate-700',
    outline: 'border border-slate-700 hover:bg-slate-800/60 text-slate-200 focus:ring-slate-500',
    ghost: 'hover:bg-slate-800/60 text-slate-300 hover:text-slate-100',
    danger: 'bg-red-600 hover:bg-red-500 text-white focus:ring-red-500 shadow-sm',
  };

  const sizes = {
    sm: 'text-xs px-2.5 py-1.5 gap-1.5',
    md: 'text-sm px-4 py-2 gap-2',
    lg: 'text-base px-5 py-2.5 gap-2.5',
  };

  return (
    <button
      className={twMerge(clsx(base, variants[variant], sizes[size], className))}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && (
        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-current" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      )}
      {children}
    </button>
  );
};
```

`frontend/src/components/ui/Input.tsx`:
```tsx
import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className, id, ...props }, ref) => {
    return (
      <div className="w-full space-y-1.5">
        {label && (
          <label htmlFor={id} className="block text-xs font-medium text-slate-300">
            {label}
          </label>
        )}
        <input
          id={id}
          ref={ref}
          className={twMerge(
            clsx(
              'w-full bg-slate-900 border border-slate-700/80 rounded-lg px-3.5 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors',
              error && 'border-red-500 focus:border-red-500 focus:ring-red-500',
              className
            )
          )}
          {...props}
        />
        {error && <p className="text-xs text-red-400">{error}</p>}
      </div>
    );
  }
);
Input.displayName = 'Input';
```

`frontend/src/components/ui/Modal.tsx`:
```tsx
import React, { useEffect } from 'react';
import { X } from 'lucide-react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  maxWidth?: string;
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  maxWidth = 'max-w-lg',
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
      <div className={`relative w-full ${maxWidth} bg-slate-900 border border-slate-800 rounded-xl shadow-2xl p-6 text-slate-100`}>
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <h3 className="text-lg font-semibold text-slate-100">{title}</h3>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 p-1 rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="mt-4">{children}</div>
      </div>
    </div>
  );
};
```

`frontend/src/components/ui/Badge.tsx`:
```tsx
import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'default', className }) => {
  const variants = {
    default: 'bg-slate-800 text-slate-300 border-slate-700',
    success: 'bg-emerald-950/60 text-emerald-400 border-emerald-800/60',
    warning: 'bg-amber-950/60 text-amber-400 border-amber-800/60',
    danger: 'bg-red-950/60 text-red-400 border-red-800/60',
    info: 'bg-indigo-950/60 text-indigo-400 border-indigo-800/60',
  };

  return (
    <span
      className={twMerge(
        clsx(
          'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border',
          variants[variant],
          className
        )
      )}
    >
      {children}
    </span>
  );
};
```

`frontend/src/components/ui/Card.tsx`:
```tsx
import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export const Card: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className, children, ...props }) => (
  <div
    className={twMerge(
      clsx('bg-slate-900/90 border border-slate-800/80 rounded-xl p-5 shadow-sm hover:border-slate-700/80 transition-all', className)
    )}
    {...props}
  >
    {children}
  </div>
);
```

- [ ] **Step 4: Executar testes**
```bash
npm test
```

- [ ] **Step 5: Commit**
```bash
git add frontend/src/contexts/ frontend/src/components/ui/
git commit -m "feat(frontend): implementar componentes de UI e ThemeContext"
```

---

### Task 4: Autenticação, Gerenciamento de Sessão e Rotas Protegidas

**Files:**
- Create: `frontend/src/contexts/AuthContext.tsx`
- Create: `frontend/src/services/auth.service.ts`
- Create: `frontend/src/components/auth/ProtectedRoute.tsx`
- Create: `frontend/src/pages/auth/LoginPage.tsx`
- Create: `frontend/src/pages/auth/RegisterPage.tsx`
- Test: `frontend/src/contexts/AuthContext.test.tsx`
- Test: `frontend/src/pages/auth/LoginPage.test.tsx`

**Interfaces:**
- Consumes: `types/auth.ts`, `services/api.ts`, `components/ui/`
- Produces: `AuthContext`, `useAuth`, `ProtectedRoute`, telas de Login e Registro.

- [ ] **Step 1: Criar testes para o fluxo de autenticação**

`frontend/src/pages/auth/LoginPage.test.tsx`:
```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { LoginPage } from './LoginPage';
import { AuthProvider } from '../../contexts/AuthContext';

describe('LoginPage', () => {
  it('renderiza os campos de email, senha e botão de entrar', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <LoginPage />
        </AuthProvider>
      </BrowserRouter>
    );

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/senha/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /entrar/i })).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Implementar `frontend/src/services/auth.service.ts`**

```typescript
import { apiFetch, setAuthTokens, clearAuthTokens } from './api';
import { User, AuthTokens } from '../types/auth';

export const authService = {
  async login(usernameOrEmail: string, password: string):Promise<AuthTokens> {
    const formData = new URLSearchParams();
    formData.append('username', usernameOrEmail);
    formData.append('password', password);

    const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData.toString(),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Falha ao autenticar');
    }

    const data: AuthTokens = await res.json();
    setAuthTokens(data.access_token, data.refresh_token);
    return data;
  },

  async register(email: string, password: string, full_name: string): Promise<User> {
    return apiFetch<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name }),
    });
  },

  async getMe(): Promise<User> {
    return apiFetch<User>('/users/me');
  },

  logout() {
    clearAuthTokens();
  },
};
```

- [ ] **Step 3: Implementar `frontend/src/contexts/AuthContext.tsx`**

```tsx
import React, { createContext, useContext, useEffect, useState } from 'react';
import { User } from '../types/auth';
import { authService } from '../services/auth.service';
import { getAccessToken } from '../services/api';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, pass: string) => Promise<void>;
  register: (email: string, pass: string, name: string) => Promise<void>;
  logout: () => void;
  hasPermission: (permission: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadUser = async () => {
      if (getAccessToken()) {
        try {
          const profile = await authService.getMe();
          setUser(profile);
        } catch {
          authService.logout();
          setUser(null);
        }
      }
      setIsLoading(false);
    };
    loadUser();
  }, []);

  const login = async (email: string, pass: string) => {
    await authService.login(email, pass);
    const profile = await authService.getMe();
    setUser(profile);
  };

  const register = async (email: string, pass: string, name: string) => {
    await authService.register(email, pass, name);
    await login(email, pass);
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  const hasPermission = (permission: string) => {
    if (!user) return false;
    if (user.is_superuser) return true;
    return user.permissions?.includes(permission) || false;
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, isLoading, login, register, logout, hasPermission }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth deve ser utilizado dentro de AuthProvider');
  return context;
};
```

- [ ] **Step 4: Implementar `ProtectedRoute.tsx`, `LoginPage.tsx` e `RegisterPage.tsx`**

`frontend/src/components/auth/ProtectedRoute.tsx`:
```tsx
import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface ProtectedRouteProps {
  requiredPermission?: string;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ requiredPermission }) => {
  const { isAuthenticated, isLoading, hasPermission } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="animate-spin h-8 w-8 border-4 border-indigo-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!isAuthenticated) return <Navigate to="/login" replace />;

  if (requiredPermission && !hasPermission(requiredPermission)) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4 text-center">
        <h2 className="text-2xl font-bold text-red-400">Acesso Restrito</h2>
        <p className="text-slate-400 mt-2">Você não possui permissão para acessar esta área ({requiredPermission}).</p>
      </div>
    );
  }

  return <Outlet />;
};
```

- [ ] **Step 5: Executar testes**
```bash
npm test
```

- [ ] **Step 6: Commit**
```bash
git add frontend/src/contexts/AuthContext.tsx frontend/src/services/auth.service.ts frontend/src/components/auth/ frontend/src/pages/auth/
git commit -m "feat(frontend): autenticacao, rotas protegidas e telas de login/registro"
```

---

### Task 5: Layout Principal da Aplicação (AppLayout, Sidebar e Header)

**Files:**
- Create: `frontend/src/components/layout/AppLayout.tsx`
- Create: `frontend/src/components/layout/Sidebar.tsx`
- Create: `frontend/src/components/layout/Header.tsx`
- Create: `frontend/src/components/layout/UserMenu.tsx`
- Test: `frontend/src/components/layout/Sidebar.test.tsx`

**Interfaces:**
- Consumes: `useAuth`, `useTheme`, `Button`, `lucide-react`
- Produces: Layout envelopador com navegação lateral, atalhos para Chat, Agentes, Bases de Conhecimento, Provedores e Admin.

- [ ] **Step 1: Criar teste de renderização da Sidebar**

`frontend/src/components/layout/Sidebar.test.tsx`:
```tsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { AuthProvider } from '../../contexts/AuthContext';

describe('Sidebar Component', () => {
  it('exibe links de navegação para Chat, Agentes e Bases', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Sidebar />
        </AuthProvider>
      </BrowserRouter>
    );

    expect(screen.getByText(/chat/i)).toBeInTheDocument();
    expect(screen.getByText(/agentes/i)).toBeInTheDocument();
    expect(screen.getByText(/base de conhecimento/i)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Implementar `Sidebar.tsx`, `Header.tsx`, `UserMenu.tsx` e `AppLayout.tsx`**

`frontend/src/components/layout/Sidebar.tsx`:
```tsx
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
          className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors mx-auto"
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
```

`frontend/src/components/layout/AppLayout.tsx`:
```tsx
import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

export const AppLayout: React.FC = () => {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-950 text-slate-100">
      <Sidebar />
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
```

- [ ] **Step 3: Executar testes**
```bash
npm test
```

- [ ] **Step 4: Commit**
```bash
git add frontend/src/components/layout/
git commit -m "feat(frontend): layout base com sidebar retratil e navegacao"
```

---

### Task 6: Módulo de Agentes de IA

**Files:**
- Create: `frontend/src/services/agents.service.ts`
- Create: `frontend/src/pages/agents/AgentsPage.tsx`
- Create: `frontend/src/components/agents/AgentCard.tsx`
- Create: `frontend/src/components/agents/AgentModal.tsx`
- Test: `frontend/src/pages/agents/AgentsPage.test.tsx`

**Interfaces:**
- Consumes: `types/agent.ts`, `services/api.ts`, `components/ui/`
- Produces: CRUD completo de Agentes, parametrização de system prompt, modelo, temperatura e vínculo com bases de conhecimento.

- [ ] **Step 1: Criar teste para a página de Agentes**

`frontend/src/pages/agents/AgentsPage.test.tsx`:
```tsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { AgentsPage } from './AgentsPage';
import { AuthProvider } from '../../contexts/AuthContext';

describe('AgentsPage', () => {
  it('exibe título e botão para criar novo agente', async () => {
    render(
      <AuthProvider>
        <AgentsPage />
      </AuthProvider>
    );

    expect(screen.getByText(/Agentes de IA/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /novo agente/i })).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Implementar `frontend/src/services/agents.service.ts`**

```typescript
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
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async delete(id: string): Promise<void> {
    return apiFetch(`/agents/${id}`, { method: 'DELETE' });
  },
};
```

- [ ] **Step 3: Implementar `AgentCard.tsx`, `AgentModal.tsx` e `AgentsPage.tsx`**

- [ ] **Step 4: Executar testes**
```bash
npm test
```

- [ ] **Step 5: Commit**
```bash
git add frontend/src/services/agents.service.ts frontend/src/pages/agents/ frontend/src/components/agents/
git commit -m "feat(frontend): modulo completo de gerenciamento de agentes de IA"
```

---

### Task 7: Módulo de Bases de Conhecimento RAG e Ingestão de Documentos

**Files:**
- Create: `frontend/src/services/kb.service.ts`
- Create: `frontend/src/pages/knowledge/KnowledgeBasesPage.tsx`
- Create: `frontend/src/pages/knowledge/KnowledgeBaseDetailPage.tsx`
- Create: `frontend/src/components/knowledge/KnowledgeBaseCard.tsx`
- Create: `frontend/src/components/knowledge/DocumentUploader.tsx`
- Test: `frontend/src/pages/knowledge/KnowledgeBasesPage.test.tsx`

**Interfaces:**
- Consumes: `types/knowledge.ts`, `services/api.ts`, `components/ui/`
- Produces: Gestão de Bases de Conhecimento, upload por drag-and-drop de `.md`, `.docx`, `.xlsx`, visualização de chunks e status de indexação.

- [ ] **Step 1: Criar testes do módulo de Knowledge Bases**

`frontend/src/pages/knowledge/KnowledgeBasesPage.test.tsx`:
```tsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { KnowledgeBasesPage } from './KnowledgeBasesPage';
import { AuthProvider } from '../../contexts/AuthContext';

describe('KnowledgeBasesPage', () => {
  it('exibe título e botão para criar base de conhecimento', () => {
    render(
      <AuthProvider>
        <KnowledgeBasesPage />
      </AuthProvider>
    );

    expect(screen.getByText(/Bases de Conhecimento/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /nova base/i })).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Implementar `frontend/src/services/kb.service.ts`**

```typescript
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
```

- [ ] **Step 3: Implementar `DocumentUploader.tsx`, `KnowledgeBaseCard.tsx`, `KnowledgeBasesPage.tsx` e `KnowledgeBaseDetailPage.tsx`**

- [ ] **Step 4: Executar testes**
```bash
npm test
```

- [ ] **Step 5: Commit**
```bash
git add frontend/src/services/kb.service.ts frontend/src/pages/knowledge/ frontend/src/components/knowledge/
git commit -m "feat(frontend): gerenciamento de bases de conhecimento RAG e upload de documentos"
```

---

### Task 8: Módulo de Provedores de IA (Credenciais e Configurações)

**Files:**
- Create: `frontend/src/services/providers.service.ts`
- Create: `frontend/src/pages/providers/ProvidersPage.tsx`
- Test: `frontend/src/pages/providers/ProvidersPage.test.tsx`

**Interfaces:**
- Consumes: `types/provider.ts`, `services/api.ts`, `components/ui/`
- Produces: Tela de cadastro e teste de credenciais para OpenRouter, OpenAI, Anthropic e Google Gemini.

- [ ] **Step 1: Criar testes da página de Provedores**
- [ ] **Step 2: Implementar `providers.service.ts` e `ProvidersPage.tsx`**
- [ ] **Step 3: Executar testes e build**
- [ ] **Step 4: Commit**
```bash
git add frontend/src/services/providers.service.ts frontend/src/pages/providers/
git commit -m "feat(frontend): modulo de configuracao de provedores de IA"
```

---

### Task 9: Módulo de Chat em Tempo Real, Streaming de Respostas e Anexos

**Files:**
- Create: `frontend/src/hooks/useChatStream.ts`
- Create: `frontend/src/services/chat.service.ts`
- Create: `frontend/src/pages/chat/ChatPage.tsx`
- Create: `frontend/src/components/chat/MessageList.tsx`
- Create: `frontend/src/components/chat/MessageItem.tsx`
- Create: `frontend/src/components/chat/ChatInput.tsx`
- Create: `frontend/src/components/chat/CodeBlock.tsx`
- Test: `frontend/src/hooks/useChatStream.test.ts`
- Test: `frontend/src/components/chat/ChatInput.test.tsx`

**Interfaces:**
- Consumes: `types/conversation.ts`, `services/api.ts`, `components/ui/`
- Produces: Chat completo em tempo real com streaming token por token, syntax highlighting e cancelamento de geração.

- [ ] **Step 1: Implementar o hook de streaming `useChatStream.ts`**

`frontend/src/hooks/useChatStream.ts`:
```typescript
import { useState, useRef, useCallback } from 'react';
import { getAccessToken } from '../services/api';

interface UseChatStreamOptions {
  onToken?: (token: string) => void;
  onComplete?: (fullContent: string) => void;
  onError?: (error: Error) => void;
}

export function useChatStream({ onToken, onComplete, onError }: UseChatStreamOptions = {}) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [streamedContent, setStreamedContent] = useState('');
  const abortControllerRef = useRef<AbortController | null>(null);

  const startStream = useCallback(async (conversationId: string, message: string, attachments?: File[]) => {
    setIsGenerating(true);
    setStreamedContent('');
    abortControllerRef.current = new AbortController();

    try {
      const token = getAccessToken();
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/conversations/${conversationId}/stream`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({ content: message }),
          signal: abortControllerRef.current.signal,
        }
      );

      if (!response.ok) throw new Error(`Erro ao iniciar streaming: ${response.statusText}`);
      if (!response.body) throw new Error('Streaming não suportado pelo navegador');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let accumulated = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        accumulated += chunk;
        setStreamedContent(accumulated);
        onToken?.(chunk);
      }

      onComplete?.(accumulated);
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        onError?.(err);
      }
    } finally {
      setIsGenerating(false);
      abortControllerRef.current = null;
    }
  }, [onToken, onComplete, onError]);

  const stopStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsGenerating(false);
    }
  }, []);

  return { isGenerating, streamedContent, startStream, stopStream };
}
```

- [ ] **Step 2: Implementar componentes do Chat (`CodeBlock`, `MessageItem`, `MessageList`, `ChatInput` e `ChatPage`)**
- [ ] **Step 3: Testar renderização de mensagens e envio de prompt**
- [ ] **Step 4: Executar testes**
```bash
npm test
```
- [ ] **Step 5: Commit**
```bash
git add frontend/src/hooks/useChatStream.ts frontend/src/services/chat.service.ts frontend/src/pages/chat/ frontend/src/components/chat/
git commit -m "feat(frontend): chat em tempo real com streaming de tokens e destaque de sintaxe"
```

---

### Task 10: Painel de Administração e RBAC (Usuários e Papéis Granulares)

**Files:**
- Create: `frontend/src/services/admin.service.ts`
- Create: `frontend/src/pages/admin/UsersAdminPage.tsx`
- Create: `frontend/src/pages/admin/RolesAdminPage.tsx`
- Create: `frontend/src/components/admin/RoleEditorModal.tsx`
- Test: `frontend/src/pages/admin/UsersAdminPage.test.tsx`

**Interfaces:**
- Consumes: `types/role.ts`, `types/auth.ts`, `services/api.ts`
- Produces: Gestão administrativa de usuários, papéis e matriz de permissões.

- [ ] **Step 1: Criar testes do painel de administração**
- [ ] **Step 2: Implementar `admin.service.ts`, `UsersAdminPage.tsx`, `RolesAdminPage.tsx` e `RoleEditorModal.tsx`**
- [ ] **Step 3: Executar testes**
```bash
npm test
```
- [ ] **Step 4: Commit**
```bash
git add frontend/src/services/admin.service.ts frontend/src/pages/admin/ frontend/src/components/admin/
git commit -m "feat(frontend): painel admin com controle de usuarios e permissoes RBAC"
```

---

### Task 11: Visualização Pública Compartilhada e Roteamento Geral da Aplicação

**Files:**
- Create: `frontend/src/pages/shared/SharedViewPage.tsx`
- Modify: `frontend/src/App.tsx`
- Test: `frontend/src/App.test.tsx`

**Interfaces:**
- Consumes: Todos os módulos anteriores
- Produces: Aplicação completa com rotas públicas (`/login`, `/register`, `/share/:slug`) e privadas sob `AppLayout`.

- [ ] **Step 1: Implementar `SharedViewPage.tsx`**
- [ ] **Step 2: Configurar todas as rotas no `App.tsx` com `react-router-dom`**
- [ ] **Step 3: Executar a suíte completa de testes e validar o build de produção**
```bash
npm test
npm run build
```
- [ ] **Step 4: Commit**
```bash
git add frontend/src/App.tsx frontend/src/pages/shared/
git commit -m "feat(frontend): integracao final de rotas e visualizacao publica compartilhada"
```
