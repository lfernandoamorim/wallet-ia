-- =============================================================================
-- Script de Criação, Atualização e Configuração do Banco de Dados: walletia
-- Data de Atualização: 01/09/2026
-- Arquivo: sql/schema-01092026.sql
-- Descrição: Estrutura completa e idempotente com tabelas, índices, extensão
--            pgvector, controle de acesso (RBAC), integração com Alembic e
--            seed do usuário administrador inicial com credenciais do .env.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. EXTENSÕES NECESSÁRIAS
-- -----------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- -----------------------------------------------------------------------------
-- 2. CONTROLE DE VERSÃO DO ALEMBIC
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

INSERT INTO alembic_version (version_num)
VALUES ('0001_initial_schema')
ON CONFLICT (version_num) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 3. TABELA DE USUÁRIOS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    username        VARCHAR(100) UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    full_name       VARCHAR(255),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    is_superadmin   BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);
CREATE INDEX IF NOT EXISTS ix_users_username ON users (username);

-- -----------------------------------------------------------------------------
-- 4. TABELAS DE ROLES E PERMISSÕES (RBAC)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS roles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(100) UNIQUE NOT NULL,
    description     TEXT,
    is_system       BOOLEAN NOT NULL DEFAULT FALSE,
    created_by      UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_roles_name ON roles (name);

CREATE TABLE IF NOT EXISTS permissions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code            VARCHAR(100) UNIQUE NOT NULL,
    description     TEXT
);

CREATE INDEX IF NOT EXISTS ix_permissions_code ON permissions (code);

CREATE TABLE IF NOT EXISTS role_permissions (
    role_id         UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id   UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE IF NOT EXISTS user_roles (
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id         UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- -----------------------------------------------------------------------------
-- 5. TABELA DE CREDENCIAIS DE PROVEDORES DE IA
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS provider_credentials (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id            UUID REFERENCES users(id) ON DELETE CASCADE, -- NULL = credencial global
    provider            VARCHAR(50) NOT NULL,                        -- 'openrouter' | 'openai' | 'anthropic' | 'gemini'
    api_key_encrypted   TEXT NOT NULL,                               -- Criptografada em repouso com Fernet
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_provider_credentials_provider ON provider_credentials (provider);
CREATE INDEX IF NOT EXISTS ix_provider_credentials_owner_id ON provider_credentials (owner_id);

-- -----------------------------------------------------------------------------
-- 6. TABELAS DE BASES DE CONHECIMENTO E DOCUMENTOS (RAG)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS knowledge_bases (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id        UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    visibility      VARCHAR(20) NOT NULL DEFAULT 'private', -- 'private' | 'shared' | 'public'
    public_slug     VARCHAR(50) UNIQUE,
    embedding_model VARCHAR(100) NOT NULL DEFAULT 'text-embedding-3-small',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_knowledge_bases_name ON knowledge_bases (name);
CREATE INDEX IF NOT EXISTS ix_knowledge_bases_owner_id ON knowledge_bases (owner_id);
CREATE INDEX IF NOT EXISTS ix_knowledge_bases_public_slug ON knowledge_bases (public_slug);

CREATE TABLE IF NOT EXISTS kb_documents (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    knowledge_base_id   UUID NOT NULL REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    file_name           VARCHAR(255) NOT NULL,
    file_type           VARCHAR(20) NOT NULL,                   -- 'md' | 'docx' | 'xlsx' | 'txt'
    storage_path        TEXT NOT NULL,
    status              VARCHAR(20) NOT NULL DEFAULT 'pending', -- 'pending' | 'processing' | 'ready' | 'error'
    error_message       TEXT,
    uploaded_by         UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_kb_documents_knowledge_base_id ON kb_documents (knowledge_base_id);

CREATE TABLE IF NOT EXISTS kb_chunks (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id         UUID NOT NULL REFERENCES kb_documents(id) ON DELETE CASCADE,
    knowledge_base_id   UUID NOT NULL REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    content             TEXT NOT NULL,
    embedding           VECTOR(1536),                            -- Vetor semântico
    metadata            JSONB,
    chunk_index         INTEGER NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_kb_chunks_kb_id ON kb_chunks (knowledge_base_id);
CREATE INDEX IF NOT EXISTS ix_kb_chunks_doc_id ON kb_chunks (document_id);
CREATE INDEX IF NOT EXISTS ix_kb_chunks_embedding_cosine ON kb_chunks USING hnsw (embedding vector_cosine_ops);

-- -----------------------------------------------------------------------------
-- 7. TABELAS DE AGENTES E PERSONAS
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS agents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id        UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    system_prompt   TEXT NOT NULL,                            -- Persona e instruções
    provider        VARCHAR(50) NOT NULL,                     -- 'openrouter' | 'openai' | 'anthropic' | 'gemini'
    model           VARCHAR(100) NOT NULL,                    -- ex: 'gpt-4o', 'claude-3-5-sonnet'
    temperature     NUMERIC(3,2) NOT NULL DEFAULT 0.70,
    max_tokens      INTEGER,
    visibility      VARCHAR(20) NOT NULL DEFAULT 'private',   -- 'private' | 'shared' | 'public'
    public_slug     VARCHAR(50) UNIQUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_agents_owner_id ON agents (owner_id);
CREATE INDEX IF NOT EXISTS ix_agents_name ON agents (name);
CREATE INDEX IF NOT EXISTS ix_agents_public_slug ON agents (public_slug);

CREATE TABLE IF NOT EXISTS agent_knowledge_bases (
    agent_id            UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    knowledge_base_id   UUID NOT NULL REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    PRIMARY KEY (agent_id, knowledge_base_id)
);

-- -----------------------------------------------------------------------------
-- 8. TABELAS DE CONVERSAS, MENSAGENS E ANEXOS (CHAT)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS conversations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id        UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    agent_id        UUID REFERENCES agents(id) ON DELETE SET NULL,
    title           VARCHAR(255),
    visibility      VARCHAR(20) NOT NULL DEFAULT 'private',   -- 'private' | 'shared' | 'public'
    public_slug     VARCHAR(50) UNIQUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_conversations_owner_id ON conversations (owner_id);
CREATE INDEX IF NOT EXISTS ix_conversations_agent_id ON conversations (agent_id);
CREATE INDEX IF NOT EXISTS ix_conversations_public_slug ON conversations (public_slug);

CREATE TABLE IF NOT EXISTS conversation_messages (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id     UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role                VARCHAR(20) NOT NULL,                 -- 'user' | 'assistant' | 'system' | 'tool'
    content             TEXT,
    tokens_input        INTEGER,
    tokens_output       INTEGER,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_conv_messages_conv_id ON conversation_messages (conversation_id);
CREATE INDEX IF NOT EXISTS ix_conv_messages_created_at ON conversation_messages (created_at);

CREATE TABLE IF NOT EXISTS message_attachments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id          UUID NOT NULL REFERENCES conversation_messages(id) ON DELETE CASCADE,
    file_name           VARCHAR(255) NOT NULL,
    mime_type           VARCHAR(100) NOT NULL,
    storage_path        TEXT NOT NULL,
    size_bytes          BIGINT,
    extracted_text      TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_message_attachments_msg_id ON message_attachments (message_id);

-- -----------------------------------------------------------------------------
-- 9. TABELA DE COMPARTILHAMENTO DE RECURSOS (POLIMÓRFICA)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS resource_shares (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resource_type   VARCHAR(50) NOT NULL,                     -- 'conversation' | 'agent' | 'knowledge_base'
    resource_id     UUID NOT NULL,
    shared_with     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    permission      VARCHAR(20) NOT NULL DEFAULT 'view',      -- 'view' | 'edit'
    shared_by       UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_resource_share UNIQUE (resource_type, resource_id, shared_with)
);

CREATE INDEX IF NOT EXISTS ix_resource_shares_resource ON resource_shares (resource_type, resource_id);
CREATE INDEX IF NOT EXISTS ix_resource_shares_shared_with ON resource_shares (shared_with);

-- -----------------------------------------------------------------------------
-- 10. DADOS INICIAIS (SEED DE PERMISSÕES E ROLES DO SISTEMA)
-- -----------------------------------------------------------------------------
INSERT INTO permissions (code, description) VALUES
    ('users.manage', 'Criar, editar, desativar usuários e atribuir roles.'),
    ('roles.manage', 'Criar, editar e excluir roles customizadas e suas permissões.'),
    ('conversations.view_own', 'Ver as próprias conversas.'),
    ('conversations.view_all', 'Ver conversas de todos os usuários (visão administrativa).'),
    ('conversations.create', 'Criar novas conversas.'),
    ('agents.view_own', 'Ver os próprios agentes.'),
    ('agents.view_all', 'Ver agentes de todos os usuários.'),
    ('agents.create', 'Criar novos agentes.'),
    ('agents.manage_all', 'Editar e excluir agentes de qualquer usuário.'),
    ('kb.view_own', 'Ver as próprias bases de conhecimento.'),
    ('kb.view_all', 'Ver bases de conhecimento de todos os usuários.'),
    ('kb.create', 'Criar base de conhecimento e subir documentos.'),
    ('kb.manage_all', 'Editar e excluir bases de conhecimento de qualquer usuário.'),
    ('sharing.manage', 'Alterar visibilidade (privado/compartilhado/público) dos próprios recursos.'),
    ('provider_credentials.manage_own', 'Cadastrar a própria chave de API de provedor.'),
    ('provider_credentials.manage_global', 'Cadastrar chaves globais do sistema.'),
    ('system.settings', 'Acessar configurações gerais do sistema.')
ON CONFLICT (code) DO NOTHING;

-- Garante a criação da Role 'admin'
INSERT INTO roles (name, description, is_system)
VALUES ('admin', 'Administrador com acesso total ao sistema', TRUE)
ON CONFLICT (name) DO NOTHING;

-- Garante a criação da Role 'user'
INSERT INTO roles (name, description, is_system)
VALUES ('user', 'Usuário padrão com acesso básico ao chat, agentes e bases', TRUE)
ON CONFLICT (name) DO NOTHING;

-- Associa todas as permissões para a role 'admin'
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
CROSS JOIN permissions p
WHERE r.name = 'admin'
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- Associa as permissões padrão para a role 'user'
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
JOIN permissions p ON p.code IN (
    'conversations.view_own',
    'conversations.create',
    'agents.view_own',
    'agents.create',
    'kb.view_own',
    'kb.create',
    'sharing.manage',
    'provider_credentials.manage_own'
)
WHERE r.name = 'user'
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 11. SEED DO USUÁRIO ADMINISTRADOR INICIAL
-- -----------------------------------------------------------------------------
-- Cria o superusuário administrador inicial se não existir, ou atualiza suas roles
INSERT INTO users (
    email,
    username,
    password_hash,
    full_name,
    is_active,
    is_superadmin
)
VALUES (
    'admin@walletia.local',
    'admin',
    crypt('AdminWalletIA@2026', gen_salt('bf', 12)),
    'Administrador do Sistema',
    TRUE,
    TRUE
)
ON CONFLICT (username) DO UPDATE
SET is_superadmin = TRUE,
    is_active = TRUE;

-- Associa o usuário admin à role 'admin'
INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id
FROM users u
CROSS JOIN roles r
WHERE u.username = 'admin' AND r.name = 'admin'
ON CONFLICT (user_id, role_id) DO NOTHING;
