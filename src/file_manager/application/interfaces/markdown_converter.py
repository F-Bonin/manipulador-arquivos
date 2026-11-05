"""Contratos para conversores de Markdown (camada de APLICAÇÃO).

Cada formato de arquivo (PDF, DOCX, planilha, TXT) terá uma classe que
cumpre o contrato MarkdownConverter. O caso de uso só conhece os contratos,
nunca as classes concretas nem as bibliotecas por trás delas.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Protocol, runtime_checkable


class MarkdownConverter(Protocol):
    """Contrato básico: quem converte um tipo de arquivo para Markdown."""

    # Extensões atendidas por este conversor, em minúsculas e com o ponto.
    # Exemplo: frozenset({".xlsx", ".xls", ".csv"})
    supported_extensions: frozenset[str]

    def convert(self, source: Path) -> str:
        """Lê o arquivo inteiro e devolve seu conteúdo em Markdown."""
        ...


@runtime_checkable
class SheetAwareConverter(MarkdownConverter, Protocol):
    """Contrato adicional para conversores de arquivos com ABAS (planilhas).

    Apenas o conversor de planilhas cumpre este contrato. Os demais
    (PDF, DOCX, TXT) não precisam saber o que é uma aba.

    O decorador @runtime_checkable permite perguntar, durante a execução,
    "este conversor entende abas?" usando isinstance().
    """

    def list_sheets(self, source: Path) -> list[str]:
        """Devolve os nomes das abas do arquivo."""
        ...

    def convert_sheets(self, source: Path, sheet_names: Sequence[str]) -> str:
        """Converte somente as abas indicadas."""
        ...