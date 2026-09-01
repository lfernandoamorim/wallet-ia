# Especificação de Design — Frontend da Plataforma Wallet IA

**Data:** 2026-09-01  
**Status:** Validado  
**Stack:** React 19 / 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, React Router DOM  
**Diretório:** `frontend/`

---

## 1. Visão Geral e Objetivos

O objetivo deste projeto é construir a interface de usuário (Frontend SPA) da **Plataforma Wallet IA**, conectando-se diretamente à API REST e serviços de tempo real do backend FastAPI.

A interface entrega uma experiência fluida, moderna e responsiva para:
1. Autenticação e gestão de sessão de usuários (JWT com refresh token).
2. Chat interativo com agentes de IA, histórico de conversas, streaming de respostas e upload de anexos.
3. Criação e parametrização de Agentes com personas customizadas, seleção de provedores (OpenRouter, OpenAI, Anthropic, Gemini) e vinculação a bases de conhecimento.
4. Gerenciamento de Bases de Conhecimento (RAG), com upload de documentos (`.md`, `.docx`, `.xlsx`), visualização de status de indexação e controle de visibilidade (privada, compartilhada, pública).
5. Configuração de credenciais de provedores de IA.
6. Painel administrativo para gestão de usuários, papéis (roles) e matriz granular de permissões (RBAC).
7. Visualização pública de chats e bases compartilhadas via slug.

---

## 2. Stack Tecnológica

| Camada | Tecnologia | Justificativa |
|---|---|---|
| **Framework Base** | React + Vite + TypeScript | Alto desempenho, tipagem estática rigorosa e agilidade de desenvolvimento para SPAs ricas em estado. |
| **Roteamento** | `react-router-dom` v6/v7 | Gerenciamento de rotas aninhadas, rotas protegidas por permissão e rotas públicas. |
| **Estilização & UI** | Tailwind CSS + Lucide Icons + Radix Primitives | Design moderno estilo SaaS de IA, alta customização e componentes acessíveis. |
| **Gerenciamento de Estado** | React Context API / Zustand | Gestão desacoplada de autenticação, tema e estado da conversa ativa. |
| **Renderização Markdown** | `react-markdown` + `remark-gfm` + Shiki/Prism | Renderização de respostas da IA com tabelas, listas e blocos de código com destaque de sintaxe e botão de cópia. |
| **Comunicação HTTP / Real-time** | Axios / Fetch nativo + SSE / WebSocket | Interceptors centralizados para injeção e refresh de JWT, além de consumo de tokens em tempo real. |

---

## 3. Arquitetura e Estrutura de Diretórios

O frontend reside inteiramente no diretório `frontend/`:

```text
frontend/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── src/
    ├── assets/              # Ícones estáticos, logos da Advance Sistemas e ilustrações
    ├── components/
    │   ├── ui/              # Componentes primitivos (Button, Input, Modal, Dropdown, Badge, Toast, Tooltip)
    │   ├── layout/          # AppLayout, Sidebar colapsável, Header, UserMenu, ThemeToggle
    │   ├── chat/            # ChatView, MessageList, MessageItem, ChatInput, FileUploadArea, CodeBlock
    │   ├── agents/          # AgentCard, AgentModal, PersonaEditor, ModelSelector
    │   ├── knowledge/       # KnowledgeBaseCard, DocumentUploader, ChunkListModal, VisibilityBadge
    │   └── admin/           # UserTable, RoleEditorModal, PermissionMatrix
    ├── contexts/
    │   ├── AuthContext.tsx  # Estado de autenticação, login, logout, refresh token
    │   └── ThemeContext.tsx # Controle de tema Dark / Light com persistência
    ├── hooks/
    │   ├── useAuth.ts       # Hook de acesso ao contexto de autenticação e permissões
    │   ├── useChatStream.ts # Hook que gerencia o ciclo de streaming de IA e acumulação de chunks
    │   └── useDebounce.ts   # Utilitário para busca em listas
    ├── pages/
    │   ├── auth/
    │   │   ├── LoginPage.tsx
    │   │   └── RegisterPage.tsx
    │   ├── chat/
    │   │   └── ChatPage.tsx
    │   ├── agents/
    │   │   └── AgentsPage.tsx
    │   ├── knowledge/
    │   │   ├── KnowledgeBasesPage.tsx
    │   │   └── KnowledgeBaseDetailPage.tsx
    │   ├── providers/
    │   │   └── ProvidersPage.tsx
    │   ├── admin/
    │   │   ├── UsersAdminPage.tsx
    │   │   └── RolesAdminPage.tsx
    │   └── shared/
    │       └── SharedViewPage.tsx
    ├── services/
    │   ├── api.ts           # Cliente HTTP com interceptors para Bearer Token e renovação
    │   ├── auth.service.ts  # Endpoints /auth/token, /auth/register, /auth/me
    │   ├── chat.service.ts  # Endpoints /conversations, envio de mensagens e streaming
    │   ├── agents.service.ts# Endpoints /agents
    │   ├── kb.service.ts    # Endpoints /knowledge-bases e upload de arquivos
    │   └── admin.service.ts # Endpoints /users e /roles
    └── types/
        ├── auth.ts          # Interfaces de User, Token, Role, Permission
        ├── agent.ts         # Interfaces de Agent, ModelConfig
        ├── conversation.ts  # Interfaces de Conversation, Message, Attachment
        └── knowledge.ts     # Interfaces de KnowledgeBase, Document, Chunk
```

---

## 4. Mapeamento de Rotas e Segurança (RBAC)

### 4.1 Rotas Públicas
* `/login` — Formulário de autenticação.
* `/register` — Registro inicial de contas.
* `/share/:slug` — Visualização pública de conversas ou bases com visibilidade pública.

### 4.2 Rotas Protegidas (dentro de `AppLayout`)
* `/` ou `/chat` — Nova conversa ou painel inicial do chat.
* `/chat/:conversationId` — Conversa ativa selecionada.
* `/agents` — Listagem e cadastro de Agentes de IA.
* `/knowledge` — Listagem de Bases de Conhecimento RAG.
* `/knowledge/:kbId` — Detalhes, documentos e upload para uma Base de Conhecimento.
* `/providers` — Gerenciamento de credenciais de IA (OpenRouter, OpenAI, Anthropic, Gemini).
* `/admin/users` — Painel administrativo de usuários (requer permissão `users:read`).
* `/admin/roles` — Painel de papéis e matriz de permissões (requer permissão `roles:read`).

### 4.3 Componente `ProtectedRoute`
Verifica a presença do token JWT no `AuthContext`. Caso inexistente ou inválido, redireciona para `/login`. Se a rota exigir uma permissão específica que o usuário não possua, exibe uma tela amigável de "Acesso Negado (403)".

---

## 5. Comunicação com a API e Streaming em Tempo Real

### 5.1 Cliente HTTP (`services/api.ts`)
* Configurado com a `baseURL` vinda da variável de ambiente `VITE_API_URL` (padrão: `http://localhost:8000`).
* Injeção automática do header `Authorization: Bearer <access_token>`.
* Tratamento centralizado de erros: renovação automática via `/auth/refresh` em caso de 401; logout e redirecionamento caso o refresh falhe.

### 5.2 Streaming do Chat (`useChatStream`)
* Conexão com o endpoint de chat via streaming (SSE / WebSocket).
* Estados gerenciados:
  * `isGenerating: boolean` — Flag que desabilita novos envios e ativa o botão "Parar Geração".
  * `streamingContent: string` — Acumulador em tempo real dos tokens parciais recebidos.
  * `typingIndicator: boolean` — Feedback visual pulsante antes do primeiro chunk.
  * `error: string | null` — Exibição de mensagens de falha com opção de tentar novamente (*retry*).

### 5.3 Upload de Arquivos
* Anexos de conversa e documentos de base de conhecimento usam `multipart/form-data`.
* Validação de tamanho e tipo de arquivo no client antes do envio.
* Indicador de progresso e status de processamento da ingestão.

---

## 6. Design System, Identidade Visual e UX

### 6.1 Paleta de Cores e Estilo
* **Tema Dark (Padrão):**
  * Fundo da Aplicação: `slate-950` (#090d16)
  * Superfícies (Sidebar, Cards, Modais): `slate-900` (#0f172a) com bordas sutis `slate-800`
  * Acento Primário: Gradiente moderno **Indigo ➔ Violet** (`#6366f1` a `#8b5cf6`)
  * Texto: `slate-100` (títulos) e `slate-400` (secundário)
* **Tema Light:**
  * Fundo: `slate-50` (#f8fafc), superfícies brancas (`#ffffff`), texto `slate-900`.
* **Tipografia:** `Inter` / `Plus Jakarta Sans` para clareza em dados e leitura técnica.

### 6.2 Micro-interações e Usabilidade
* Transições suaves de tema (Dark/Light).
* Animações sutis de entrada para modais e mensagens do chat.
* Atalhos de teclado: `Enter` envia prompt, `Shift + Enter` quebra linha, `Esc` fecha diálogos.
* Suporte a Drag & Drop para upload de arquivos.

---

## 7. Estratégia de Testes e Validação

1. **Testes Unitários de Componentes:** Testes com `vitest` e `@testing-library/react` para componentes de UI isolados (botões, inputs, modais, renderizador de markdown).
2. **Testes de Fluxo e Hooks:** Validação dos hooks `useAuth` e `useChatStream` com mock de respostas de rede e streaming.
3. **Validação de Build:** `npm run build` / `vite build` executado sem erros de compilação ou de tipos TypeScript.
