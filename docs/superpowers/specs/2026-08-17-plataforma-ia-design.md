# Design Doc: Plataforma de Chat com IA, Agentes e Base de Conhecimento

## 1. Visão Geral
Este projeto é uma plataforma self-hosted para criação de agentes de IA, RAG (Base de Conhecimento) e chat em tempo real, baseada nas especificações inspiradas no Odysseus. Abrangeremos inicialmente a Fase 1 (MVP) e a Fase 2 (Roles customizadas e RBAC avançado).

## 2. Decisões Arquiteturais e Tecnologias
- **Linguagem**: Python 3.12+ (Gestão de ambiente e dependências via `uv`).
- **Backend API**: FastAPI.
- **Banco de Dados**: PostgreSQL 16 com extensão `pgvector`. ORM: SQLAlchemy 2.0 (async) + Alembic.
- **Pub/Sub e Fila**: Redis 7.
- **Worker Assíncrono**: `Arq` (nativamente assíncrono para integração fluida com o ecossistema async do FastAPI).
- **Frontend**: SPA desenvolvido em React com Vite.
- **Arquitetura Lógica**: 3 Camadas (Diretiva, Orquestração, Execução) organizadas por Domínio/Feature (Alta Coesão).

## 3. Estrutura do Backend (3 Camadas por Domínio)
O projeto Python será organizado agrupando as responsabilidades por domínio (ex: `users`, `agents`, `conversations`, `knowledge_bases`).
Para manter a altíssima coesão e baixo acoplamento, a estrutura dentro de cada domínio seguirá estritamente a Arquitetura de 3 Camadas requerida:

```text
backend/
├── app/
│   ├── core/
│   │   ├── config.py         # Configurações Pydantic Settings
│   │   ├── security.py       # JWT, hashing
│   │   └── database.py       # Configuração da sessão do SQLAlchemy
│   │
│   ├── domains/
│   │   ├── auth/
│   │   ├── users/
│   │   ├── agents/
│   │   │   ├── directive.py      # Routers FastAPI, validações Pydantic de entrada/saída
│   │   │   ├── orchestration.py  # Regras de negócio, verificação de RBAC, montagem de contexto
│   │   │   └── execution.py      # SQLAlchemy models, repositórios (acesso DB) e integração de Providers
│   │   │
│   │   ├── conversations/
│   │   └── knowledge_bases/
│   │
│   └── main.py                   # Ponto de entrada da aplicação, inclusão das rotas
```

### Regras das Camadas:
- **Diretiva**: Recebe as requisições (HTTP/WebSocket), faz a validação inicial dos dados (Schemas Pydantic) e injeta as dependências para a Orquestração. Não possui regra de negócio.
- **Orquestração**: O "cérebro" da operação. Executa lógicas complexas, checa permissões do usuário, coordena os diferentes fluxos (ex: preparar o prompt RAG).
- **Execução**: Realiza as operações de infraestrutura. Interage diretamente com o Banco de Dados (ORM/Models) e faz chamadas para serviços externos (OpenAI, OpenRouter, Storage).

## 4. Componentes Principais

### 4.1. Autenticação e RBAC (Fase 1 e 2)
- Login gerando token JWT.
- A orquestração checa dinamicamente permissões associadas às roles do usuário para todas as operações sensíveis, permitindo customização robusta (Fase 2).

### 4.2. Chat e Streaming
- Uso de WebSockets em `directive.py` do domínio `conversations`.
- O Redis Pub/Sub repassará os tokens gerados pelos modelos de LLM (Execução) para a fila, a Orquestração formata e a Diretiva devolve via WebSocket em tempo real.

### 4.3. RAG e Background Worker (Arq)
- Upload de arquivos é gerenciado pela Diretiva e persistido fisicamente na Execução.
- A Orquestração agenda um job no `Arq` (Redis).
- O Worker do Arq (rodando em processo separado) executa a extração (`.md`, `.docx`, etc), aplica o chunking, requisita o embedding, e persiste no `pgvector`.

### 4.4. Frontend (React/Vite)
- Inicializado separadamente. Será consumido exclusivamente por APIs REST para dados e WebSocket para streaming.
