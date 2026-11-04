"""Montagem das peças do programa ("composition root").

Este é o ÚNICO lugar que conhece, ao mesmo tempo, os casos de uso e as
implementações concretas. Todas as outras partes recebem o que precisam
já pronto.

Quando precisarmos trocar uma biblioteca, mudamos aqui e em mais nenhum lugar.
"""

from __future__ import annotations

from file_manager.application.use_cases.split_pdf import SplitPdfUseCase
from file_manager.infrastructure.config.settings import Settings
from file_manager.infrastructure.pdf.pypdf_splitter import PypdfSplitter


def build_split_pdf_use_case(settings: Settings) -> SplitPdfUseCase:
    """Cria o caso de uso de separar PDF já com suas dependências."""
    return SplitPdfUseCase(
        splitter=PypdfSplitter(),
        output_dir=settings.output_dir,
    )