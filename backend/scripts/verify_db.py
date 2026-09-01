"""Script para verificar o estado e integridade do banco de dados."""

import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import core.models
from core.database import AsyncSessionLocal
from sqlalchemy import text


async def verify_db():
    async with AsyncSessionLocal() as session:
        # Tabelas existentes
        res_tables = await session.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
        )
        tables = [r[0] for r in res_tables.fetchall()]
        print(f"[OK] Total de tabelas públicas: {len(tables)}")
        for t in tables:
            print(f"  - {t}")

        # Versão alembic
        if "alembic_version" in tables:
            res_ver = await session.execute(text("SELECT version_num FROM alembic_version"))
            version = res_ver.scalar()
            print(f"[OK] Versao Alembic atual: {version}")

        # Total de permissões
        if "permissions" in tables:
            res_p = await session.execute(text("SELECT count(*) FROM permissions"))
            print(f"[OK] Permissoes cadastradas: {res_p.scalar()}")

        # Total de roles
        if "roles" in tables:
            res_r = await session.execute(text("SELECT count(*) FROM roles"))
            print(f"[OK] Roles cadastradas: {res_r.scalar()}")

        # Usuários
        if "users" in tables:
            res_u = await session.execute(text("SELECT username, email, is_superadmin, is_active FROM users"))
            print("[OK] Usuarios:")
            for u in res_u.fetchall():
                print(f"  - {u[0]} ({u[1]}) | Superadmin: {u[2]} | Ativo: {u[3]}")


if __name__ == "__main__":
    asyncio.run(verify_db())
