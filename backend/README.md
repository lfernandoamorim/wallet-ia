# Wallet IA — Backend API

Backend da Plataforma Wallet IA construído em FastAPI, SQLAlchemy 2.0 Async, PostgreSQL + pgvector e arquitetura em 3 camadas (Directive, Orchestration, Execution).

## Como Executar

1. **Sincronizar Dependências:**
   ```bash
   uv sync
   ```

2. **Aplicar Migrações do Banco:**
   ```bash
   uv run alembic upgrade head
   ```

3. **Iniciar o Servidor de Desenvolvimento:**
   ```bash
   uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Executar Testes:**
   ```bash
   uv run pytest
   ```
