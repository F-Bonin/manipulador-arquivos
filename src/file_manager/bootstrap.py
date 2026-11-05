"""Montagem das peças do programa ("composition root").

Este é o ÚNICO lugar que conhece, ao mesmo tempo, os casos de uso e as
implementações concretas. Todas as outras partes recebem o que precisam
já pronto.

Para suportar um novo formato de arquivo, basta criar o conversor e
adicioná-lo à lista em build_convert_to_markdown_use_case.
"""

from __future__ import annotations

from file_manager.application.use_cases.convert_to_markdown import ConvertToMarkdownUseCase
from file_manager.application.use_cases.split_pdf import SplitPdfUseCase
from file_manager.infrastructure.config.settings import Settings
from file_manager.infrastructure.converters.docx_converter import DocxToMarkdownConverter
from file_manager.infrastructure.converters.pdf_converter import PdfToMarkdownConverter
from file_manager.infrastructure.converters.spreadsheet_converter import (
    SpreadsheetToMarkdownConverter,
)
from file_manager.infrastructure.converters.text_converter import TextToMarkdownConverter
from file_manager.infrastructure.pdf.pypdf_splitter import PypdfSplitter


def build_split_pdf_use_case(settings: Settings) -> SplitPdfUseCase:
    """Cria o caso de uso de separar PDF já com suas dependências."""
    return SplitPdfUseCase(
        splitter=PypdfSplitter(),
        output_dir=settings.output_dir,
    )


def build_convert_to_markdown_use_case(settings: Settings) -> ConvertToMarkdownUseCase:
    """Cria o caso de uso de converter para Markdown com todos os conversores."""
    converters = [
        TextToMarkdownConverter(),
        SpreadsheetToMarkdownConverter(),
        DocxToMarkdownConverter(),
        PdfToMarkdownConverter(),
    ]
    return ConvertToMarkdownUseCase(
        converters=converters,
        output_dir=settings.output_dir,
        large_output_chars=settings.large_output_warning_chars,
    )