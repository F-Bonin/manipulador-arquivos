"""Contrato para separadores de PDF (camada de APLICAÇÃO).

Um Protocol define "o que precisa existir" sem dizer "como funciona".
Qualquer classe que tenha um método `split` com esta assinatura cumpre o
contrato, sem precisar herdar de nada.

Assim o caso de uso não depende de nenhuma biblioteca: hoje usamos o pypdf,
amanhã podemos trocar por outra, e o caso de uso continua igual.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol


class PdfSplitter(Protocol):
    """Contrato: quem separa PDFs por página."""

    def split(self, source: Path, destination_dir: Path) -> list[Path]:
        """Separa o PDF em um arquivo por página.

        Args:
            source: caminho do PDF original.
            destination_dir: pasta onde as páginas serão gravadas.

        Returns:
            Lista dos arquivos gerados, na ordem das páginas originais.
        """
        ...