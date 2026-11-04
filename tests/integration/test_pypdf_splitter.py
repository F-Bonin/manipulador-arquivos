"""Testes de integração do PypdfSplitter.

Aqui usamos a biblioteca pypdf de verdade e criamos PDFs reais temporários.
"""

from pathlib import Path

import pytest
from pypdf import PdfReader, PdfWriter

from file_manager.domain.exceptions.errors import CorruptedPdfError
from file_manager.infrastructure.pdf.pypdf_splitter import PypdfSplitter


def _create_pdf(path: Path, pages: int) -> None:
    """Cria um PDF de teste com `pages` páginas em branco.

    Cada página tem uma largura diferente (100, 200, 300...). Assim, depois
    da separação, a largura de cada página prova qual era a sua posição
    no documento original.
    """
    writer = PdfWriter()
    for number in range(1, pages + 1):
        writer.add_blank_page(width=100 * number, height=200)
    with open(path, "wb") as stream:
        writer.write(stream)


def test_split_creates_one_file_per_page_in_original_order(tmp_path: Path):
    """Um PDF de 5 páginas gera 5 arquivos de 1 página, na ordem original."""
    source = tmp_path / "original.pdf"
    _create_pdf(source, pages=5)

    files = PypdfSplitter().split(source, tmp_path / "saida")

    assert len(files) == 5
    for position, file in enumerate(files, start=1):
        reader = PdfReader(file)
        assert len(reader.pages) == 1
        # A largura identifica a página: a 1ª tem 100, a 2ª tem 200...
        assert int(reader.pages[0].mediabox.width) == 100 * position


def test_split_names_files_with_zero_padded_page_numbers(tmp_path: Path):
    """Os nomes seguem a paginação original: _pagina_001, _pagina_002..."""
    source = tmp_path / "relatorio.pdf"
    _create_pdf(source, pages=3)

    files = PypdfSplitter().split(source, tmp_path / "saida")

    assert [file.name for file in files] == [
        "relatorio_pagina_001.pdf",
        "relatorio_pagina_002.pdf",
        "relatorio_pagina_003.pdf",
    ]


def test_split_raises_for_corrupted_pdf(tmp_path: Path):
    """Um arquivo .pdf que não é um PDF de verdade gera CorruptedPdfError."""
    source = tmp_path / "quebrado.pdf"
    source.write_bytes(b"isto nao e um pdf")

    with pytest.raises(CorruptedPdfError):
        PypdfSplitter().split(source, tmp_path / "saida")