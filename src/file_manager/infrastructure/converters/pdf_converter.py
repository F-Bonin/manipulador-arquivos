"""Conversor de PDF para Markdown (camada de INFRAESTRUTURA).

Usa a biblioteca pymupdf4llm, que detecta títulos, listas e tabelas e gera
um Markdown estruturado.

Modo clássico: as versões novas da biblioteca usam por padrão um "modo
layout" (com modelo de inteligência artificial e arquivos compilados extras).
Aqui desativamos esse modo e usamos o clássico, que é mais leve e não
depende desses arquivos extras.

Importante: esta versão lê apenas o texto que já existe no PDF. PDFs
escaneados (só imagem) retornam vazio e serão tratados na fase de OCR.
"""

from __future__ import annotations

from pathlib import Path

from file_manager.domain.exceptions.errors import ConversionError


class PdfToMarkdownConverter:
    """Converte arquivos .pdf em Markdown."""

    supported_extensions = frozenset({".pdf"})

    def convert(self, source: Path) -> str:
        try:
            # Import "tardio": a biblioteca é pesada. Importando aqui dentro, os
            # outros recursos (como separar PDF) continuam rápidos para abrir.
            import pymupdf4llm

            # getattr busca o comando use_layout se ele existir. Assim, o código
            # também funciona com versões antigas da biblioteca, que não o têm
            # (e que já usam o modo clássico).
            use_layout = getattr(pymupdf4llm, "use_layout", None)
            if use_layout is not None:
                use_layout(False)  # False = modo clássico

            return pymupdf4llm.to_markdown(str(source))
        except Exception as error:
            # Arquivo corrompido, protegido por senha, biblioteca bloqueada etc.
            raise ConversionError(f"Não foi possível converter o PDF: {error}") from error