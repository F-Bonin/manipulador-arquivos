"""Testes unitários do caso de uso SplitPdfUseCase.

Usamos um separador FALSO (FakeSplitter) no lugar do pypdf. Isso prova que
o caso de uso funciona só com o contrato, sem depender de biblioteca alguma.
"""

from pathlib import Path

import pytest

from file_manager.application.use_cases.split_pdf import SplitPdfUseCase
from file_manager.domain.exceptions.errors import InvalidFileError


class FakeSplitter:
    """Separador falso: não separa nada, só registra que foi chamado."""

    def __init__(self) -> None:
        self.calls: list[tuple[Path, Path]] = []

    def split(self, source: Path, destination_dir: Path) -> list[Path]:
        self.calls.append((source, destination_dir))
        return [destination_dir / "pagina_1.pdf", destination_dir / "pagina_2.pdf"]


def test_execute_returns_result_and_calls_splitter(tmp_path: Path):
    """Com um PDF válido, o caso de uso chama o separador e devolve o resultado."""
    # tmp_path é uma pasta temporária criada pelo pytest para cada teste.
    source = tmp_path / "documento.pdf"
    source.write_bytes(b"%PDF-1.4")  # conteúdo mínimo: o fake não lê o arquivo
    output_dir = tmp_path / "saida"
    splitter = FakeSplitter()

    result = SplitPdfUseCase(splitter, output_dir).execute(source)

    assert len(splitter.calls) == 1
    assert result.total_pages == 2
    assert result.output_dir.parent == output_dir
    assert result.output_dir.name.startswith("documento_paginas_")


def test_execute_raises_when_file_does_not_exist(tmp_path: Path):
    """Arquivo inexistente deve gerar InvalidFileError."""
    use_case = SplitPdfUseCase(FakeSplitter(), tmp_path / "saida")

    with pytest.raises(InvalidFileError):
        use_case.execute(tmp_path / "nao_existe.pdf")


def test_execute_raises_when_file_is_not_pdf(tmp_path: Path):
    """Arquivo que não é PDF deve ser recusado, sem chamar o separador."""
    source = tmp_path / "texto.txt"
    source.write_text("olá")
    splitter = FakeSplitter()

    with pytest.raises(InvalidFileError):
        SplitPdfUseCase(splitter, tmp_path / "saida").execute(source)

    assert splitter.calls == []