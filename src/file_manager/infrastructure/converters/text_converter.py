"""Conversor de arquivos TXT para Markdown (camada de INFRAESTRUTURA)."""

from __future__ import annotations

from pathlib import Path

from file_manager.infrastructure.converters.text_file_reader import read_text_file


class TextToMarkdownConverter:
    """Converte arquivos .txt em Markdown.

    Um texto simples já é um Markdown válido, então apenas lemos o conteúdo
    (acertando a codificação) e padronizamos as quebras de linha.
    """

    supported_extensions = frozenset({".txt"})

    def convert(self, source: Path) -> str:
        text = read_text_file(source)
        # O Windows usa \r\n para quebrar linha; padronizamos para \n.
        return text.replace("\r\n", "\n").replace("\r", "\n").strip()