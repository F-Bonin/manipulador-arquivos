"""Separador de PDF baseado na biblioteca pypdf (camada de INFRAESTRUTURA).

Esta classe cumpre o contrato PdfSplitter. É aqui, e somente aqui, que o
programa conhece a biblioteca pypdf.
"""

from __future__ import annotations

from pathlib import Path

from pypdf import PasswordType, PdfReader, PdfWriter
from pypdf.errors import PdfReadError

from file_manager.domain.exceptions.errors import (
    CorruptedPdfError,
    EncryptedPdfError,
)

# Quantidade mínima de dígitos no número da página (001, 002...).
# Garante que a ordenação alfabética dos arquivos siga a ordem das páginas.
_MIN_DIGITS = 3


class PypdfSplitter:
    """Separa um PDF em um arquivo por página usando o pypdf."""

    def split(self, source: Path, destination_dir: Path) -> list[Path]:
        """Grava cada página do PDF em um arquivo separado.

        Os arquivos seguem a numeração original: a página 7 do documento
        vira `<nome>_pagina_007.pdf`.

        Raises:
            CorruptedPdfError: PDF ilegível, danificado ou sem páginas.
            EncryptedPdfError: PDF protegido por senha.
        """
        try:
            # O arquivo é aberto em modo binário ("rb") e mantido aberto
            # só durante o processamento. O pypdf lê as páginas sob demanda,
            # então PDFs grandes não são carregados inteiros na memória.
            with open(source, "rb") as stream:
                reader = PdfReader(stream)

                # PDFs criptografados precisam ser desbloqueados antes de ler.
                # Tentamos senha vazia: alguns PDFs são "protegidos" apenas
                # contra edição, mas abrem sem senha.
                if reader.is_encrypted:
                    if reader.decrypt("") == PasswordType.NOT_DECRYPTED:
                        raise EncryptedPdfError(
                            "O PDF está protegido por senha e não pôde ser aberto."
                        )

                total_pages = len(reader.pages)
                if total_pages == 0:
                    raise CorruptedPdfError("O PDF não possui nenhuma página.")

                # Só criamos a pasta depois de confirmar que o PDF é válido,
                # evitando deixar pastas vazias quando há erro.
                destination_dir.mkdir(parents=True, exist_ok=True)

                digits = max(_MIN_DIGITS, len(str(total_pages)))
                generated: list[Path] = []

                # enumerate(..., start=1) numera as páginas a partir de 1,
                # igual à numeração que as pessoas veem no PDF.
                for page_number, page in enumerate(reader.pages, start=1):
                    output_file = (
                        destination_dir
                        / f"{source.stem}_pagina_{page_number:0{digits}d}.pdf"
                    )

                    # Um PdfWriter novo por página: o arquivo gerado
                    # contém somente aquela página.
                    writer = PdfWriter()
                    writer.add_page(page)
                    with open(output_file, "wb") as output_stream:
                        writer.write(output_stream)

                    generated.append(output_file)

                return generated

        except PdfReadError as error:
            # Traduz o erro técnico da biblioteca para um erro do nosso
            # domínio. "from error" preserva a causa original para depuração.
            raise CorruptedPdfError(
                f"Não foi possível ler o PDF (arquivo corrompido?): {error}"
            ) from error