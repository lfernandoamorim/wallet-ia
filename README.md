# Plataforma Wallet IA 🚀

Plataforma corporativa self-hosted de **Inteligência Artificial Generativa**, **Chat em Tempo Real**, **Agentes Parametrizáveis** e **Recuperação Aumentada por Geração (RAG)** com **Controle de Acesso Granular (RBAC)**.

> 📖 **Especificação Completa:** Consulte o documento canônico [`SPEC.md`](file:///D:/Projetos/AdvanceSistemas/wallet-ia/SPEC.md) para detalhes arquiteturais profundos, modelo de dados DDL/ORM, matriz de permissões e catálogo de APIs.

---

## 🛠️ Stack Tecnológica

- **Backend:** Python 3.12+, FastAPI, Uvicorn, SQLAlchemy 2.0 (Async), Alembic, Pydantic v2.
- **Banco de Dados & Vetores:** PostgreSQL 16 com extensão `pgvector` (SQLite assíncrono para suíte de testes).
- **Segurança:** Autenticação JWT (Access + Refresh Tokens) com criptografia `bcrypt` e RBAC granular.
- **Gerenciador de Dependências Python:** `uv` (Astral).
- **Frontend SPA:** React 18/19, TypeScript, Vite, Tailwind CSS, Lucide Icons, React Router DOM.
- **Testes Automatizados:** Pytest, Pytest-Asyncio, HTTPX, Vitest.

---

## 📋 Pré-requisitos

Certifique-se de ter as seguintes ferramentas instaladas no seu ambiente:

1. **Python 3.12+**
2. **`uv`** — Gerenciador de pacotes e ambientes virtuais Python:
   ```bash
   # Windows (PowerShell)
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

   # Linux/macOS
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. **PostgreSQL 16+** com extensão `pgvector` (ou container Docker).
4. **Node.js 18+** e **npm** (para execução da interface web React).

---

## ⚙️ Configuração do Ambiente

### 1. Clonar o Repositório e Criar o Arquivo `.env`
Copie o arquivo de exemplo para criar a sua configuração local:
```bash
cp .env.example .env
```

Edite o arquivo `.env` para ajustar suas credenciais de banco e chaves de segurança:
```env
# Banco de Dados PostgreSQL com pgvector
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/appdb

# Autenticação e Criptografia
SECRET_KEY=sua_chave_secreta_jwt_super_segura
ENCRYPTION_KEY=J1d_5m0lV8kG7t9_x6w2P3r7Y1q0z8N5L4m3K2j1H0g=

# Redis (Streaming Pub/Sub, Cache e Fila)
REDIS_URL=redis://localhost:6379/0

# Armazenamento Local de Anexos
STORAGE_PATH=./storage
```

### 2. Instalar as Dependências do Backend
Utilize o `uv` para sincronizar automaticamente o ambiente virtual e as dependências:
```bash
uv sync
```

### 3. Executar as Migrações do Banco de Dados
Aplique o versionamento do esquema de banco de dados via Alembic:
```bash
uv run alembic upgrade head
```

---

## 🚀 Como Executar o Projeto

### 1. Executando o Backend (API FastAPI)
Inicie o servidor de desenvolvimento com reload automático:
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- **API Base:** `http://localhost:8000`
- **Documentação Swagger Interativa:** `http://localhost:8000/docs`
- **Documentação Redoc:** `http://localhost:8000/redoc`
- **Health Check:** `http://localhost:8000/health`

### 2. Executando o Frontend (React + Vite)
Navegue até o diretório `frontend/`, instale as dependências e inicie o servidor Vite:
```bash
cd frontend
npm install
npm run dev
```
- **Aplicação Web:** `http://localhost:3000` (ou porta indicada no terminal)

---

## 🧪 Como Executar os Testes

### Backend (Pytest)
Para rodar toda a suíte de testes unitários e de integração do backend:
```bash
uv run pytest
```
Para rodar com verbosidade detalhada:
```bash
uv run pytest -v
```

### Frontend (Vitest)
Para rodar os testes da interface:
```bash
cd frontend
npm run test
```

---

## 📁 Estrutura do Projeto

```text
wallet-ia/
├── SPEC.md                             # Especificação técnica e arquitetural canônica
├── README.md                           # Guia de início rápido e instruções de execução
├── pyproject.toml                      # Configuração de dependências Python (uv)
├── alembic.ini                         # Configurações do Alembic
│
├── app/                                # Código-fonte do Backend (Arquitetura em 3 Camadas)
│   ├── core/                           # Núcleo compartilhado (config, database, security, RBAC)
│   │   ├── config.py                   # Pydantic Settings
│   │   ├── database.py                 # Engine assíncrono e sessões
│   │   ├── security.py                 # Criptografia bcrypt e tokens JWT
│   │   ├── permissions.py              # Catálogo de códigos de permissão
│   │   └── models.py                   # Registro central dos modelos ORM
│   │
│   └── domains/                        # Módulos de Domínio (Directive -> Orchestration -> Execution)
│       ├── auth/                       # Autenticação e sessão
│       ├── users/                      # Gestão de usuários e superadmin
│       ├── roles/                      # Papéis e matriz de permissões RBAC
│       ├── providers/                  # Credenciais de provedores (OpenRouter, OpenAI, etc.)
│       ├── knowledge_bases/            # RAG, ingestão (.md, .docx, .xlsx) e busca vetorial
│       ├── agents/                     # Agentes com persona e modelos
│       └── conversations/              # Chat interativo, streaming SSE e compartilhamento
│
├── frontend/                           # Aplicação Web SPA (React + TypeScript + Tailwind)
│   ├── src/
│   │   ├── components/                 # Componentes reutilizáveis (UI, Layout, Chat, Agentes)
│   │   ├── contexts/                   # AuthContext e ThemeContext
│   │   ├── pages/                      # Telas da aplicação (Login, Chat, Admin, etc.)
│   │   └── services/                   # Clientes HTTP e SSE
│
├── migrations/                         # Migrações versionadas do banco (Alembic)
├── tests/                              # Suíte de testes automatizados
└── docs/                               # Planos de implementação e histórico de design
```

---

## 🌿 Fluxo de Desenvolvimento Git

- O desenvolvimento de novas funcionalidades e correções deve sempre ocorrer em branches de funcionalidade separadas (ex: `feature/<nome-da-feature>`).
- O branch `main` permanece reservado para versões estáveis e releases aprovadas.
