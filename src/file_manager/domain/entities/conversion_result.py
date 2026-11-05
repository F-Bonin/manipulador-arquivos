"""Resultado de uma conversão para Markdown (camada de DOMÍNIO)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ConversionResult:
    """Descreve o que aconteceu após converter um arquivo para Markdown."""

    source_file: Path     # Arquivo original (PDF, DOCX, planilha ou TXT)
    output_file: Path     # Arquivo .md gerado
    character_count: int  # Quantidade de caracteres do Markdown gerado

    # Avisos para o usuário (ex.: resultado muito grande).
    # Tupla vazia significa "nenhum aviso". Precisa ficar por último porque
    # tem um valor padrão.
    warnings: tuple[str, ...] = ()