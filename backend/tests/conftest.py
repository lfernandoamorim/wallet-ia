"""Configuração e fixtures globais do pytest."""

import pytest
import core.models  # Garante registro de todos os modelos ORM


@pytest.fixture(autouse=True)
def setup_models():
    """Garante que todos os modelos ORM estejam registrados."""
    pass
