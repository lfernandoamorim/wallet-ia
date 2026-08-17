# Especificação Técnica — Plataforma de Chat com IA, Agentes e Base de Conhecimento

> Documento de referência para o desenvolvimento. Inspirado nos requisitos e features do projeto **Odysseus** (self-hosted AI workspace — https://github.com/odysseus-dev/odysseus), adaptado para stack **Python + PostgreSQL + Redis**, com RBAC avançado (roles customizadas) e modelo de visibilidade privado/compartilhado/público.

---

## 1. Visão Geral

### 1.1 Objetivo
Construir uma plataforma self-hosted onde o usuário:
1. Faz login no sistema.
2. Conversa com agentes de IA via chat (texto + upload de arquivos na conversa).
3. As conversas ficam persistidas e organizadas por usuário.
4. Pode criar **agentes** com **persona** (system prompt) e conectá-los a diferentes provedores de IA (OpenRouter, OpenAI, Anthropic, Google Gemini).
5. Pode criar uma **base de conhecimento** (RAG) subindo arquivos `.md`, `.doc/.docx`, `.xlsx`, que é usada pelos agentes como contexto adicional.
6. Um **admin** gerencia usuários, define quem é admin, cria **roles personalizadas** com permissões granulares, e enxerga todos os recursos do sistema (conversas, agentes, KBs). Usuários não-admin só veem os próprios recursos, salvo o que for compartilhado com eles.
7. Cada recurso (conversa, agente, base de conhecimento) pode ter visibilidade **privada**, **compartilhada** (usuários específicos) ou **pública** (qualquer um com o link).

### 1.2 Referência (Odysseus) — o que inspira este projeto
O Odysseus é um workspace de IA self-hosted (Docker Compose, `docker compose up`) com: chat + agentes (local/API, tools, MCP, arquivos), pesquisa profunda, comparação de modelos, editor de documentos, e-mail, notas/tarefas/calendário, galeria, temas, upload de arquivos, 2FA. Deste conjunto, o nosso projeto foca no **núcleo** que você pediu: **chat + agentes com persona + anexos + base de conhecimento (RAG) + múltiplos provedores + administração/RBAC + compartilhamento**. Os demais módulos (e-mail, calendário, pesquisa profunda, editor de documentos) ficam registrados no roadmap como evolução futura (seção 17), mas não são escopo da v1.

### 1.3 Fora de escopo (v1)
- Execução de modelos locais (LLM local via llama.cpp/MLX) — v1 é 100% via API de provedores externos.
- Integração de e-mail (IMAP/SMTP), calendário (CalDAV), notas/tarefas.
- Editor de documentos colaborativo.
- MCP (Model Context Protocol) e "tools"/shell para o agente — pode entrar em v2.

---

## 2. Arquitetura de Alto Nível

```
                         ┌──────────────────────┐
                         │      Frontend         │
                         │ (SPA – React/Vue, ou  │
                         │  Jinja2 + HTMX)        │
                         └──────────┬────────────┘
                                    │ HTTPS / WSS
                         ┌──────────▼────────────┐
                         │   API Backend (Python) │
                         │   FastAPI + Uvicorn    │
                         │  REST + WebSocket      │
                         └───┬────────┬───────┬───┘
                              │        │       │
                 ┌────────────┘        │       └─────────────┐
                 │                     │                      │
        ┌────────▼───────┐   ┌────────▼────────┐   ┌─────────▼─────────┐
        │  PostgreSQL     │   │      Redis       │   │  Worker (Celery/  │
        │  + pgvector     │   │ (pub/sub chat,   │   │  RQ / Arq)         │
        │  (dados + RAG)  │   │  cache, filas,   │   │  ingestão de KB,  │
        │                 │   │  sessão)         │   │  embeddings, jobs  │
        └─────────────────┘   └──────────────────┘   └─────────┬──────────┘
                                                                 │
                                                     ┌───────────▼───────────┐
                                                     │  Object Storage        │
                                                     │  (S3 / MinIO / disco)  │
                                                     │  anexos + arquivos KB  │
                                                     └────────────────────────┘

        ┌─────────────────────────────────────────────────────────┐
        │  Camada de Provedores de IA (adapter/gateway único)      │
        │  OpenRouter | OpenAI | Anthropic | Google Gemini          │
        └─────────────────────────────────────────────────────────┘
```

### 2.1 Componentes
| Componente | Responsabilidade |
|---|---|
| **API Backend** | Auth, CRUD, orquestração do chat, RBAC, endpoints REST + WebSocket |
| **PostgreSQL** | Dados relacionais (usuários, roles, conversas, mensagens, agentes) + `pgvector` para embeddings da base de conhecimento |
| **Redis** | Pub/Sub para streaming de respostas do chat em tempo real, cache de sessão, fila leve, rate limiting |
| **Worker assíncrono** | Processamento pesado fora do request-response: parsing de `.doc/.xlsx/.md`, chunking, geração de embeddings, indexação |
| **Object Storage** | Armazenamento binário dos arquivos (anexos de conversa e documentos da base de conhecimento) — local em disco no MVP, S3-compatível (MinIO) recomendado para produção |
| **Gateway de Provedores de IA** | Camada única que abstrai chamadas para OpenRouter/OpenAI/Anthropic/Gemini, normalizando streaming, tokens, tool calls |

---

## 3. Stack Tecnológico

| Camada | Tecnologia | Observação |
|---|---|---|
| Linguagem | Python 3.12+ | |
| Framework API | **FastAPI** | Async nativo, WebSocket, tipagem via Pydantic, ideal para streaming de chat |
| ORM | **SQLAlchemy 2.0 (async)** + **Alembic** | Migrations versionadas |
| Banco de dados | **PostgreSQL 16** + extensão **pgvector** | Um único banco para dados relacionais e vetores (evita depender de um vector DB externo como Supabase/Qdrant) |
| Cache / Pub-Sub | **Redis 7** | Streaming de tokens do chat, sessões, filas leves |
| Fila / Jobs assíncronos | **Celery** (com Redis como broker) ou **Arq** (mais leve, async nativo) | Ingestão de documentos da base de conhecimento, geração de embeddings |
| Autenticação | **JWT (access + refresh token)** via `python-jose`/`pyjwt`, senha com `passlib[bcrypt]` | Sessão via cookie httpOnly ou Bearer token |
| Parsing de documentos | `markdown-it-py` (.md), `python-docx` (.docx/.doc), `openpyxl` (.xlsx) | Extração de texto para RAG |
| Embeddings | Configurável por provedor (OpenAI `text-embedding-3-small`, ou modelo local via `sentence-transformers` como fallback) | Guardado em `vector` column do pgvector |
| Chamadas a LLMs | SDKs oficiais: `openai`, `anthropic`, `google-generativeai`, além de client HTTP genérico para **OpenRouter** (compatível com API OpenAI) | Camada de abstração própria (seção 11) |
| Storage de arquivos | `boto3` (S3-compatível) ou filesystem local | MinIO recomendado em self-hosted |
| Frontend | React (Vite) ou Vue 3, **ou** server-rendered com Jinja2 + HTMX + Alpine.js para simplificar o MVP | Este documento assume SPA, mas a API é agnóstica |
| Containerização | Docker + docker-compose (seguindo o padrão do Odysseus: `docker compose up -d --build`) | |
| Testes | `pytest`, `pytest-asyncio`, `httpx` | |

---

## 4. Modelo de Dados

### 4.1 Diagrama conceitual (entidades principais)

```
users ──< user_roles >── roles ──< role_permissions >── permissions
  │                                                            
  ├──< conversations >── conversation_messages
  │         │
  │         └──< message_attachments
  │
  ├──< agents >── agent_knowledge_bases >── knowledge_bases
  │                                              │
  ├──< knowledge_bases                           └──< kb_documents ──< kb_chunks (vector)
  │
  ├──< resource_shares  (polimórfico: conversation | agent | knowledge_base)
  │
  └──< provider_credentials  (chave de API por provedor, por usuário ou global)
```

### 4.2 Tabelas principais (DDL simplificado)

```sql
-- Usuários
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           TEXT UNIQUE NOT NULL,
    username        TEXT UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    full_name       TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    is_superadmin   BOOLEAN NOT NULL DEFAULT FALSE,  -- flag de admin "raiz", separado do sistema de roles
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Roles (inclui as padrão "admin" e "user" + roles customizadas criadas pelo admin)
CREATE TABLE roles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT UNIQUE NOT NULL,        -- ex: "admin", "user", "editor_kb", "suporte"
    description     TEXT,
    is_system       BOOLEAN NOT NULL DEFAULT FALSE, -- TRUE para "admin"/"user" (não podem ser apagadas)
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Permissões granulares (catálogo fixo, mantido em código + seed no banco)
CREATE TABLE permissions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code            TEXT UNIQUE NOT NULL,   -- ex: "users.manage", "conversations.view_all", "kb.create"
    description     TEXT
);

CREATE TABLE role_permissions (
    role_id         UUID REFERENCES roles(id) ON DELETE CASCADE,
    permission_id   UUID REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE user_roles (
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    role_id         UUID REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- Agentes (persona + configuração de modelo)
CREATE TABLE agents (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id            UUID REFERENCES users(id) ON DELETE CASCADE,
    name                TEXT NOT NULL,
    description         TEXT,
    system_prompt       TEXT NOT NULL,          -- a "persona"
    provider            TEXT NOT NULL,           -- 'openrouter' | 'openai' | 'anthropic' | 'gemini'
    model               TEXT NOT NULL,           -- ex: 'gpt-4.1', 'claude-sonnet-4-6', 'gemini-2.5-pro'
    temperature         NUMERIC(3,2) DEFAULT 0.7,
    max_tokens          INTEGER,
    visibility          TEXT NOT NULL DEFAULT 'private', -- 'private' | 'shared' | 'public'
    public_slug         TEXT UNIQUE,             -- usado quando visibility = 'public'
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Vínculo agente <-> bases de conhecimento (N:N)
CREATE TABLE agent_knowledge_bases (
    agent_id            UUID REFERENCES agents(id) ON DELETE CASCADE,
    knowledge_base_id   UUID REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    PRIMARY KEY (agent_id, knowledge_base_id)
);

-- Bases de conhecimento
CREATE TABLE knowledge_bases (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id        UUID REFERENCES users(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    description     TEXT,
    visibility      TEXT NOT NULL DEFAULT 'private',
    public_slug     TEXT UNIQUE,
    embedding_model TEXT NOT NULL DEFAULT 'text-embedding-3-small',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Documentos enviados para a base de conhecimento
CREATE TABLE kb_documents (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    knowledge_base_id   UUID REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    file_name           TEXT NOT NULL,
    file_type           TEXT NOT NULL,         -- 'md' | 'docx' | 'xlsx'
    storage_path         TEXT NOT NULL,         -- caminho no object storage
    status               TEXT NOT NULL DEFAULT 'pending', -- pending|processing|ready|error
    error_message        TEXT,
    uploaded_by          UUID REFERENCES users(id),
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Chunks vetorizados (RAG)
CREATE TABLE kb_chunks (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id         UUID REFERENCES kb_documents(id) ON DELETE CASCADE,
    knowledge_base_id   UUID REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    content             TEXT NOT NULL,
    embedding           VECTOR(1536),          -- dimensão conforme o modelo de embedding escolhido
    metadata            JSONB,                  -- ex: {"sheet": "Plan1", "row_range": "1-40"} para xlsx
    chunk_index         INTEGER NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX kb_chunks_embedding_idx ON kb_chunks USING hnsw (embedding vector_cosine_ops);

-- Conversas
CREATE TABLE conversations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id        UUID REFERENCES users(id) ON DELETE CASCADE,
    agent_id        UUID REFERENCES agents(id),
    title           TEXT,
    visibility      TEXT NOT NULL DEFAULT 'private',
    public_slug     TEXT UNIQUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE conversation_messages (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id     UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role                TEXT NOT NULL,          -- 'user' | 'assistant' | 'system' | 'tool'
    content             TEXT,
    tokens_input        INTEGER,
    tokens_output       INTEGER,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE message_attachments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id          UUID REFERENCES conversation_messages(id) ON DELETE CASCADE,
    file_name           TEXT NOT NULL,
    mime_type           TEXT NOT NULL,
    storage_path        TEXT NOT NULL,
    size_bytes          BIGINT,
    extracted_text       TEXT,                   -- texto extraído (se aplicável) para dar contexto ao LLM
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Compartilhamento granular (para visibility = 'shared')
CREATE TABLE resource_shares (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resource_type   TEXT NOT NULL,   -- 'conversation' | 'agent' | 'knowledge_base'
    resource_id     UUID NOT NULL,
    shared_with     UUID REFERENCES users(id) ON DELETE CASCADE,
    permission      TEXT NOT NULL DEFAULT 'view', -- 'view' | 'edit'
    shared_by       UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (resource_type, resource_id, shared_with)
);

-- Credenciais de provedores de IA (chave própria por usuário, ou chave global do sistema)
CREATE TABLE provider_credentials (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id        UUID REFERENCES users(id) ON DELETE CASCADE, -- NULL = credencial global do sistema
    provider        TEXT NOT NULL,   -- 'openrouter' | 'openai' | 'anthropic' | 'gemini'
    api_key_encrypted TEXT NOT NULL, -- criptografado com Fernet/KMS, nunca em texto puro
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

> **Nota sobre `visibility`**: os três estados (`private`, `shared`, `public`) valem para `conversations`, `agents` e `knowledge_bases`. `shared` depende da tabela `resource_shares` (lista de usuários convidados). `public` gera um `public_slug` (UUID curto/slug) que permite acesso via URL direta, sem exigir que o visitante esteja logado (opcionalmente pode exigir login — configurável).

---

## 5. Autenticação, Autorização e RBAC

### 5.1 Autenticação
- Login por e-mail/usuário + senha (bcrypt).
- JWT: `access_token` (curta duração, ex. 15 min) + `refresh_token` (httpOnly cookie, ex. 7 dias).
- 2FA (TOTP) pode entrar como melhoria (o Odysseus tem isso) — registrar no roadmap.
- Não há **self-signup** por padrão: o admin é quem cria os usuários (conforme requisito da tela de administração). Isso pode ser configurável (`ALLOW_SELF_SIGNUP=false` por padrão).

### 5.2 Modelo de permissões (RBAC com roles customizadas)
Ao invés de um booleano simples `is_admin`, o sistema usa um catálogo de **permissões** (`permissions`), agrupadas em **roles** (`roles`), atribuídas a usuários (`user_roles`, N:N — um usuário pode ter mais de uma role).

Duas roles de sistema (`is_system = true`, não podem ser excluídas):
- **admin** — todas as permissões.
- **user** — permissões básicas de uso (ver seção 5.3).

O admin pode criar **roles customizadas** (ex.: "Gestor de Conhecimento", "Suporte N1") e escolher, via UI (checkboxes), quais permissões cada role tem, a partir do catálogo abaixo.

### 5.3 Catálogo de permissões sugerido

| Código | Descrição |
|---|---|
| `users.manage` | Criar, editar, desativar usuários; atribuir roles |
| `roles.manage` | Criar/editar/excluir roles customizadas e suas permissões |
| `conversations.view_own` | Ver as próprias conversas |
| `conversations.view_all` | Ver conversas de todos os usuários (visão de admin) |
| `conversations.create` | Criar conversas |
| `agents.view_own` / `agents.view_all` | Ver agentes próprios / de todos |
| `agents.create` | Criar agentes |
| `agents.manage_all` | Editar/excluir agentes de qualquer usuário |
| `kb.view_own` / `kb.view_all` | Ver bases de conhecimento próprias / de todos |
| `kb.create` | Criar base de conhecimento e subir documentos |
| `kb.manage_all` | Editar/excluir bases de conhecimento de qualquer usuário |
| `sharing.manage` | Alterar visibilidade (privado/compartilhado/público) dos próprios recursos |
| `provider_credentials.manage_own` | Cadastrar a própria chave de API de provedor |
| `provider_credentials.manage_global` | Cadastrar chaves globais do sistema (usadas quando o usuário não tem chave própria) |
| `system.settings` | Acessar configurações gerais do sistema |

A role **user** por padrão recebe: `conversations.view_own`, `conversations.create`, `agents.view_own`, `agents.create`, `kb.view_own`, `kb.create`, `sharing.manage`, `provider_credentials.manage_own`.
A role **admin** recebe todas.

### 5.4 Regra de visibilidade no `WHERE` das queries
```
SE usuário tem permissão "*.view_all" (conversations/agents/kb)
    → retorna todos os registros
SENÃO
    → retorna registros onde owner_id = usuário
       OU existe em resource_shares (shared_with = usuário)
       OU visibility = 'public'
```

---

## 6. Painel de Administração

Tela acessível apenas para usuários com `users.manage` (por padrão, a role `admin`).

### 6.1 Gestão de usuários
- Listar usuários (nome, e-mail, roles, status ativo/inativo, data de criação).
- Criar usuário: nome, e-mail, senha temporária (ou envio de convite por e-mail), seleção de uma ou mais **roles**.
- Editar usuário: ativar/desativar, resetar senha, alterar roles.
- Nunca permitir que o próprio admin remova a última role `admin` do sistema (guarda-costas para não travar o sistema sem admin).

### 6.2 Gestão de roles customizadas
- Listar roles (sistema + customizadas).
- Criar role: nome, descrição, seleção de permissões via checkboxes (catálogo da seção 5.3).
- Editar/excluir role customizada (roles de sistema não podem ser excluídas).
- Visualizar quantos usuários estão em cada role.

### 6.3 Visão administrativa de recursos
- Aba "Conversas" (todas, filtrável por usuário/agente/data).
- Aba "Agentes" (todos).
- Aba "Bases de Conhecimento" (todas, com status de processamento dos documentos).
- Aba "Configurações do sistema": chaves de API globais dos provedores, parâmetros gerais (limite de upload, modelo de embedding padrão etc.).

---

## 7. Agentes e Persona

### 7.1 Criação de agente
Campos: nome, descrição, **system prompt (persona)**, provedor (`openrouter|openai|anthropic|gemini`), modelo, temperatura, max_tokens, bases de conhecimento vinculadas (N:N), visibilidade.

### 7.2 Execução (pipeline de uma mensagem)
1. Usuário envia mensagem (+ anexos opcionais) numa conversa vinculada a um agente.
2. Backend monta o **prompt final**:
   - `system_prompt` do agente (persona).
   - Se o agente tem KB vinculada: busca top-K chunks relevantes via similaridade vetorial (`pgvector`, cosine) usando a mensagem do usuário como query → injeta como contexto ("Use as informações abaixo se forem relevantes: ...").
   - Texto extraído de anexos da mensagem atual (se houver).
   - Histórico da conversa (últimas N mensagens, respeitando a janela de contexto do modelo).
3. Chama o **Gateway de Provedores** (seção 11) com streaming ativado.
4. Tokens streamados via WebSocket para o frontend, e a mensagem completa é persistida em `conversation_messages` ao final.

---

## 8. Chat em Tempo Real

### 8.1 Transporte
- **WebSocket** (`/ws/conversations/{id}`) para envio de mensagens e recebimento de tokens em streaming.
- Alternativa mais simples para MVP: **Server-Sent Events (SSE)** em vez de WebSocket, já que o fluxo é majoritariamente unidirecional (servidor → cliente). WebSocket é recomendado se quiser evoluir para colaboração/typing indicators.

### 8.2 Papel do Redis
- Cada resposta do LLM em streaming é publicada em um canal Redis Pub/Sub (`chat:conversation:{id}`) — isso permite múltiplas instâncias do backend (escalonamento horizontal) sem perder mensagens, e permite reconexão do cliente sem perder o stream em andamento.
- Redis também guarda o **estado momentâneo do streaming** (buffer parcial) com TTL curto, e é usado para **rate limiting** (mensagens por usuário/minuto) e **presença** (se for necessário indicar "digitando...").

### 8.3 Upload de arquivos na conversa
- Endpoint `POST /conversations/{id}/messages` aceita `multipart/form-data` com texto + arquivo(s).
- Arquivo é salvo no object storage; se for um tipo com texto extraível (pdf, docx, txt, csv, imagens via OCR opcional), o texto é extraído de forma **assíncrona** (worker) e anexado ao contexto da próxima chamada ao LLM. Para respostas mais rápidas, arquivos pequenos podem ser processados de forma síncrona no próprio request.
- Tipos aceitos e tamanho máximo configuráveis (`MAX_UPLOAD_MB`, `ALLOWED_ATTACHMENT_TYPES`).

---

## 9. Base de Conhecimento (RAG)

### 9.1 Fluxo de ingestão
```
Upload (.md / .doc|.docx / .xlsx)
      │
      ▼
kb_documents (status = pending) + arquivo salvo no storage
      │
      ▼  (job assíncrono no worker)
Extração de texto:
  - .md      → markdown-it-py / leitura direta
  - .docx    → python-docx (parágrafos, tabelas)
  - .xlsx    → openpyxl (por planilha/aba, célula a célula ou por linha)
      │
      ▼
Chunking (ex.: ~500-800 tokens por chunk, overlap de ~10-15%)
      │
      ▼
Geração de embeddings (modelo configurável por KB)
      │
      ▼
Inserção em kb_chunks (vector) + kb_documents.status = ready
```

### 9.2 Busca (retrieval)
- Query do usuário → embedding → `SELECT ... ORDER BY embedding <=> :query_embedding LIMIT k` (operador de distância do pgvector).
- Filtro obrigatório por `knowledge_base_id` (das bases vinculadas ao agente).
- Top-K configurável por agente (padrão: 5).
- Opcional (v2): busca híbrida (full-text search do Postgres + vetorial) para melhorar recall.

### 9.3 Tratamento de erros de conversão
- `.doc` (formato binário antigo) exige LibreOffice headless (`soffice --headless --convert-to docx`) ou biblioteca equivalente antes do `python-docx`, já que este só lê `.docx`. Documentar essa dependência de sistema no Dockerfile.
- Documentos que falham (`status = error`) devem mostrar `error_message` legível na UI para o usuário tentar novamente.

---

## 10. Anexos (Attachments) — regras gerais

- Aplicam-se tanto a mensagens de chat quanto a documentos de base de conhecimento, mas em tabelas separadas (`message_attachments` vs `kb_documents`) porque o ciclo de vida é diferente (anexo de chat é contextual/efêmero à mensagem; documento de KB é indexado permanentemente).
- Armazenamento sempre fora do banco (object storage), o banco guarda apenas metadados e caminho.
- Antivírus/validação de MIME type real (não confiar apenas na extensão) — usar `python-magic` para checar o conteúdo do arquivo.
- Política de retenção e exclusão: ao excluir uma conversa ou documento, excluir também o arquivo físico correspondente (job de limpeza).

---

## 11. Integração com Provedores de IA (OpenRouter, OpenAI, Anthropic, Gemini)

### 11.1 Camada de abstração (Gateway)
Criar uma interface única, por exemplo:

```python
class ChatProvider(Protocol):
    async def stream_chat(
        self,
        messages: list[Message],
        model: str,
        temperature: float,
        max_tokens: int | None,
    ) -> AsyncIterator[str]:
        ...
```

Implementações concretas: `OpenRouterProvider`, `OpenAIProvider`, `AnthropicProvider`, `GeminiProvider`, cada uma traduzindo o formato de mensagens interno para o formato exigido pela respectiva API, e normalizando o streaming de volta para um formato comum de "chunks de texto".

- **OpenRouter**: API compatível com o formato OpenAI (`/chat/completions`), permite acessar dezenas de modelos (incluindo Anthropic e Google) por uma única chave — útil como "provider catch-all" e para comparação de custo.
- **OpenAI**: SDK oficial `openai`, streaming via `stream=True`.
- **Anthropic**: SDK oficial `anthropic`, streaming via `client.messages.stream(...)`.
- **Gemini**: SDK oficial `google-generativeai`, streaming via `generate_content(..., stream=True)`.

### 11.2 Seleção de credenciais
Ordem de resolução da chave de API usada numa chamada:
1. Chave própria do usuário dono do agente (`provider_credentials.owner_id = user`), se cadastrada.
2. Senão, chave global do sistema (`provider_credentials.owner_id IS NULL`) cadastrada pelo admin.
3. Senão, erro amigável orientando o usuário/admin a cadastrar uma chave.

Chaves sempre armazenadas **criptografadas em repouso** (Fernet com chave mestra em variável de ambiente, ou integração com um KMS/Vault se disponível).

### 11.3 Padronização de erros
Mapear erros específicos de cada provedor (rate limit, chave inválida, modelo inexistente, contexto excedido) para um conjunto padronizado de erros da aplicação, exibidos de forma consistente na UI.

---

## 12. API REST — Endpoints Principais

```
Auth
POST   /auth/login
POST   /auth/refresh
POST   /auth/logout

Usuários & Roles (admin)
GET    /admin/users
POST   /admin/users
PATCH  /admin/users/{id}
GET    /admin/roles
POST   /admin/roles
PATCH  /admin/roles/{id}
DELETE /admin/roles/{id}
GET    /admin/permissions

Agentes
GET    /agents
POST   /agents
GET    /agents/{id}
PATCH  /agents/{id}
DELETE /agents/{id}
POST   /agents/{id}/share
PATCH  /agents/{id}/visibility

Bases de Conhecimento
GET    /knowledge-bases
POST   /knowledge-bases
GET    /knowledge-bases/{id}
DELETE /knowledge-bases/{id}
POST   /knowledge-bases/{id}/documents        (upload .md/.doc/.xlsx)
GET    /knowledge-bases/{id}/documents
DELETE /knowledge-bases/{id}/documents/{doc_id}
PATCH  /knowledge-bases/{id}/visibility

Conversas
GET    /conversations
POST   /conversations
GET    /conversations/{id}
DELETE /conversations/{id}
PATCH  /conversations/{id}/visibility
POST   /conversations/{id}/messages           (texto + anexos, multipart)
GET    /conversations/{id}/messages
WS     /ws/conversations/{id}                 (streaming)

Público (sem necessidade de dono, respeita visibility='public')
GET    /public/conversations/{slug}
GET    /public/agents/{slug}
GET    /public/knowledge-bases/{slug}

Provedores
GET    /provider-credentials
POST   /provider-credentials
DELETE /provider-credentials/{id}
```

---

## 13. Segurança

- HTTPS obrigatório em produção (Traefik/Nginx como proxy reverso com TLS — mesmo padrão usado por você em outros projetos self-hosted).
- Rate limiting por usuário/IP (Redis) nos endpoints de chat e login.
- Sanitização de entrada e output (evitar XSS ao renderizar Markdown das respostas do LLM no frontend).
- Isolamento estrito de dados por `owner_id` em todas as queries (nunca confiar em filtro só no frontend).
- Logs de auditoria para ações administrativas (criação/alteração de usuários e roles, mudança de visibilidade para `public`).
- Nunca expor `api_key` de provedores em respostas de API, nem em logs.

---

## 14. Backup e Restore

Inspirado no `backup-restore.md` do Odysseus, adaptado à stack Postgres/Redis/Object Storage:

- **Banco de dados**: `pg_dump` agendado (cron ou job do worker) para dump lógico completo (schema + dados, incluindo `kb_chunks` com os vetores). Retenção configurável (ex. últimos 7 diários + 4 semanais).
- **Object storage**: backup incremental dos arquivos (anexos + documentos de KB) — `rsync`/`mc mirror` se MinIO, ou snapshot do volume Docker.
- **Redis**: não precisa de backup persistente (dados voláteis: streaming state, cache, sessões) — mas se usado como broker de fila, garantir que jobs pendentes sejam reprocessáveis (idempotência dos workers).
- **Restore**: documentar passo a passo — `pg_restore`, restauração dos arquivos, e um script de verificação de integridade (checar se todo `storage_path` referenciado no banco existe fisicamente).
- Exportar/Importar "pacote" de um recurso isolado (ex.: exportar um agente + sua KB para importar em outra instância) pode ser uma funcionalidade v2, similar ao conceito de "agent migration" do Odysseus.

---

## 15. Estrutura de Pastas Sugerida (Backend Python)

```
app/
├── api/
│   ├── v1/
│   │   ├── auth.py
│   │   ├── admin_users.py
│   │   ├── admin_roles.py
│   │   ├── agents.py
│   │   ├── knowledge_bases.py
│   │   ├── conversations.py
│   │   └── ws_chat.py
├── core/
│   ├── config.py            # settings via pydantic-settings
│   ├── security.py          # JWT, hashing, criptografia de chaves
│   └── permissions.py       # decorators/dependencies de RBAC
├── db/
│   ├── base.py
│   ├── session.py
│   └── models/
│       ├── user.py
│       ├── role.py
│       ├── agent.py
│       ├── knowledge_base.py
│       └── conversation.py
├── providers/
│   ├── base.py
│   ├── openrouter.py
│   ├── openai_provider.py
│   ├── anthropic_provider.py
│   └── gemini_provider.py
├── rag/
│   ├── extractors/          # md.py, docx.py, xlsx.py
│   ├── chunking.py
│   └── retrieval.py
├── workers/
│   ├── celery_app.py        # ou arq_app.py
│   └── tasks/
│       ├── ingest_document.py
│       └── cleanup_files.py
├── schemas/                 # Pydantic (request/response)
└── main.py

alembic/
docker-compose.yml
Dockerfile
requirements.txt
.env.example
```

---

## 16. Variáveis de Ambiente (exemplo `.env.example`)

```
# App
SECRET_KEY=
ALLOW_SELF_SIGNUP=false
MAX_UPLOAD_MB=25
ALLOWED_ATTACHMENT_TYPES=pdf,txt,csv,md,docx,xlsx,png,jpg

# Banco de dados
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/appdb

# Redis
REDIS_URL=redis://redis:6379/0

# Storage (S3-compatível)
STORAGE_ENDPOINT=
STORAGE_BUCKET=
STORAGE_ACCESS_KEY=
STORAGE_SECRET_KEY=

# Provedores (globais/opcional — usuário pode sobrepor com chave própria)
OPENROUTER_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GEMINI_API_KEY=

# Criptografia de credenciais salvas no banco
CREDENTIALS_ENCRYPTION_KEY=
```

---

## 17. Roadmap de Desenvolvimento (fases)

### Fase 1 — MVP
- Auth (login, JWT), CRUD de usuários pelo admin, roles fixas (admin/user).
- CRUD de agentes (persona + provedor + modelo).
- Chat com streaming (1 provedor funcionando de ponta a ponta, ex. OpenAI, depois os demais).
- Upload de anexos em conversa (sem extração avançada, só anexar e mostrar).
- Base de conhecimento: upload `.md`, ingestão, busca vetorial básica, vínculo com agente.

### Fase 2 — RBAC avançado e compartilhamento
- Roles customizadas + catálogo de permissões + tela de administração completa.
- Modelo de visibilidade privado/compartilhado/público em conversas, agentes e KB.
- Suporte a `.docx` e `.xlsx` na base de conhecimento.

### Fase 3 — Robustez e operação
- Backup/restore automatizado.
- Múltiplos provedores completos (OpenRouter, Anthropic, Gemini) com seleção de credencial por usuário.
- Rate limiting, auditoria, 2FA.

### Fase 4 — Evoluções (inspiradas no Odysseus, fora do escopo inicial)
- Deep Research (pesquisa multi-step na web).
- Comparação lado a lado entre modelos.
- Editor de documentos colaborativo.
- Notas/tarefas/calendário, e-mail.
- Tools/MCP para os agentes (execução de ações externas).

---

## 18. Checklist de Requisitos (rastreabilidade com o que foi pedido)

- [x] Backend em Python (FastAPI).
- [x] PostgreSQL como banco principal (+ pgvector para RAG).
- [x] Redis para o chat (pub/sub de streaming, cache, filas).
- [x] Usuário acessa o sistema e conversa com IA via chat; conversas persistidas.
- [x] Upload de arquivos na conversa (anexos).
- [x] Área de base de conhecimento com upload de `.md`, `.doc`, `.xlsx`.
- [x] Criação de agentes com persona (system prompt).
- [x] Conexão com OpenRouter, OpenAI, Anthropic e Gemini.
- [x] Tela de administração: admin cria usuários e define se são admin.
- [x] Usuário não-admin só vê seus próprios recursos; admin vê tudo.
- [x] Visibilidade privada / compartilhada / pública por conversa, agente e base de conhecimento.
- [x] Admin pode criar roles personalizadas para outros usuários.
