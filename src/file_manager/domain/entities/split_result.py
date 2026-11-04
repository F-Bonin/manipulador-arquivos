"""Resultado de uma separação de PDF (camada de DOMÍNIO).

Esta entidade é Python puro: não usa nenhuma biblioteca externa.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SplitResult:
    """Descreve o que aconteceu após separar um PDF.

    frozen=True deixa o objeto imutável: depois de criado, não muda.
    """

    source_file: Path             # PDF original que foi separado
    output_dir: Path              # Pasta onde as páginas foram gravadas
    page_files: tuple[Path, ...]  # Um arquivo por página, na ordem original

    @property
    def total_pages(self) -> int:
        """Quantidade de páginas geradas (igual à do PDF original)."""
        return len(self.page_files)