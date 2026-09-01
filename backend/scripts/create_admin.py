"""Script para criação e provisionamento do usuário administrador inicial no banco de dados."""

import asyncio
import os
import sys
from pathlib import Path

# Adiciona o diretório backend ao sys.path para importação de módulos
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import core.models  # Garante o mapeamento de todos os modelos ORM
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.database import AsyncSessionLocal
from core.security import get_password_hash
from domains.roles.execution import Role
from domains.roles.orchestration import seed_permissions_and_roles
from domains.users.execution import User


async def create_or_update_admin(
    username: str,
    email: str,
    password: str,
    full_name: str = "Administrador do Sistema",
) -> None:
    """Cria ou atualiza as credenciais de um usuário administrador no banco de dados."""
    async with AsyncSessionLocal() as session:
        # 1. Garante que roles e permissões existam no banco
        await seed_permissions_and_roles(session)

        # 2. Busca a role 'admin'
        res_role = await session.execute(
            select(Role).where(Role.name == "admin").options(selectinload(Role.permissions))
        )
        admin_role = res_role.scalars().first()

        # 3. Verifica se o usuário já existe
        res_user = await session.execute(
            select(User)
            .where((User.username == username) | (User.email == email))
            .options(selectinload(User.roles))
        )
        user = res_user.scalars().first()

        if user:
            print(f"[+] Atualizando usuário existente: {user.username} ({user.email})")
            user.username = username
            user.email = email
            user.password_hash = get_password_hash(password)
            user.full_name = full_name
            user.is_active = True
            user.is_superadmin = True
            if admin_role and admin_role not in user.roles:
                user.roles.append(admin_role)
        else:
            print(f"[+] Criando novo usuário administrador: {username} ({email})")
            user = User(
                username=username,
                email=email,
                password_hash=get_password_hash(password),
                full_name=full_name,
                is_active=True,
                is_superadmin=True,
                roles=[admin_role] if admin_role else [],
            )
            session.add(user)

        await session.commit()
        print(f"[OK] Usuario administrador '{username}' provisionado com sucesso!")


if __name__ == "__main__":
    admin_user = os.getenv("ADMIN_USERNAME", "admin")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@walletia.local")
    admin_pass = os.getenv("ADMIN_PASSWORD", "AdminWalletIA@2026")

    print(f"Provisionando usuário '{admin_user}' ({admin_email})...")
    asyncio.run(create_or_update_admin(admin_user, admin_email, admin_pass))
