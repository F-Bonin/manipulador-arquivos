"""Caso de uso: separar um PDF por páginas (camada de APLICAÇÃO).

O caso de uso orquestra o trabalho: valida a entrada, decide o destino e
delega a parte técnica para o separador (PdfSplitter). Ele não sabe qual
biblioteca está por trás dele.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from file_manager.application.interfaces.pdf_splitter import PdfSplitter
from file_manager.domain.entities.split_result import SplitResult
from file_manager.domain.exceptions.errors import InvalidFileError


class SplitPdfUseCase:
    """Separa um PDF em vários arquivos, um por página."""

    def __init__(self, splitter: PdfSplitter, output_dir: Path) -> None:
        """Recebe as dependências já prontas (injeção de dependência).

        Args:
            splitter: objeto que realmente separa o PDF (cumpre o contrato).
            output_dir: pasta base onde os resultados serão criados.
        """
        self._splitter = splitter
        self._output_dir = output_dir

    def execute(self, source: Path) -> SplitResult:
        """Executa a separação.

        Args:
            source: caminho do PDF a ser separado.

        Returns:
            SplitResult com a pasta de saída e os arquivos gerados.

        Raises:
            InvalidFileError: se o arquivo não existir ou não for um PDF.
        """
        self._validate(source)
        destination = self._build_destination(source)

        # A parte técnica é delegada ao separador (infraestrutura).
        page_files = self._splitter.split(source, destination)

        return SplitResult(
            source_file=source,
            output_dir=destination,
            page_files=tuple(page_files),
        )

    @staticmethod
    def _validate(source: Path) -> None:
        """Confere se o caminho aponta para um arquivo PDF existente."""
        if not source.is_file():
            raise InvalidFileError(f"Arquivo não encontrado: {source}")
        if source.suffix.lower() != ".pdf":
            raise InvalidFileError(
                f"O arquivo precisa ser um PDF (.pdf), mas recebi '{source.suffix}'."
            )

    def _build_destination(self, source: Path) -> Path:
        """Define uma pasta única para este resultado.

        Exemplo: output/contrato_paginas_20261104_170512
        O carimbo de data e hora evita misturar com resultados anteriores
        e nunca sobrescreve nada.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self._output_dir / f"{source.stem}_paginas_{timestamp}"