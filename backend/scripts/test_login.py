"""Script para testar e validar o login com as credenciais criadas."""

import asyncio
import os
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import core.models  # Garante o mapeamento de todos os modelos ORM
from core.database import AsyncSessionLocal
from domains.auth import orchestration


async def test_auth():
    admin_user = os.getenv("ADMIN_USERNAME", "admin")
    admin_pass = os.getenv("ADMIN_PASSWORD", "AdminWalletIA@2026")

    async with AsyncSessionLocal() as session:
        user = await orchestration.authenticate_user(session, admin_user, admin_pass)
        if not user:
            print("[ERRO] Falha na autenticacao.")
            return False

        auth_data = orchestration.login_for_access_token(user)
        print("[OK] Autenticacao realizada com sucesso!")
        print(f"Usuario: {user.username} ({user.email})")
        print(f"Superadmin: {user.is_superadmin}")
        print(f"Permissoes: {len(auth_data['user']['permissions'])}")
        print(f"Access Token: {auth_data['access_token'][:30]}...")
        return True


if __name__ == "__main__":
    success = asyncio.run(test_auth())
    if not success:
        sys.exit(1)
