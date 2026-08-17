"""Testes unitários para a camada de execução (modelos ORM) do domínio de usuários."""

from app.domains.users.execution import User


def test_user_model_instantiation() -> None:
    """Verifica a instanciação correta do modelo User e seus atributos."""
    user = User(
        email="test@test.com",
        username="testuser",
        password_hash="hash_secreto",
    )
    assert user.email == "test@test.com"
    assert user.username == "testuser"
    assert user.password_hash == "hash_secreto"


def test_user_model_defaults_and_table_name() -> None:
    """Verifica nome da tabela e valores padrão definidos no modelo User."""
    assert User.__tablename__ == "users"
    user = User(
        email="admin@test.com",
        username="admin",
        password_hash="admin_hash",
    )
    # Atributos com default no Column
    assert user.is_active is None or user.is_active is True
    assert user.is_superadmin is None or user.is_superadmin is False
