"""Testes para o domínio de Base de Conhecimento e RAG (extração, chunking e busca)."""

import io
import pytest
from app.domains.knowledge_bases.orchestration import (
    extract_text_from_file,
    split_text_into_chunks,
    cosine_similarity,
)


def test_extract_markdown_text():
    """Testa extração de texto de arquivo markdown."""
    content = b"# Titulo de Teste\n\nEste e um conteudo de documentacao RAG."
    extracted = extract_text_from_file("documento.md", content)
    assert "Titulo de Teste" in extracted
    assert "conteudo de documentacao RAG" in extracted


def test_chunking_with_overlap():
    """Testa divisão de texto longo em chunks com sobreposição."""
    text = "Palavra " * 200
    chunks = split_text_into_chunks(text, chunk_size=150, overlap=30)
    assert len(chunks) > 1
    assert all(len(c) <= 200 for c in chunks)


def test_cosine_similarity():
    """Testa cálculo de similaridade por cosseno."""
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]
    assert pytest.approx(cosine_similarity(v1, v2), 0.001) == 1.0
    assert pytest.approx(cosine_similarity(v1, v3), 0.001) == 0.0
