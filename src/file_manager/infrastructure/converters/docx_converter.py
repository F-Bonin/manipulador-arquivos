"""Conversor de documentos Word (DOCX) para Markdown.

Camada de INFRAESTRUTURA.

O que é convertido:
  - Títulos (Título e Título 1 a 6) -> # ... ######
  - Listas com marcadores          -> - item
  - Tabelas                        -> tabelas Markdown
  - Parágrafos                     -> texto simples

Limitações desta primeira versão:
  - Negrito, itálico e links viram texto simples.
  - Imagens são ignoradas.
  - Listas numeradas "reais" do Word viram listas com marcadores.
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

from file_manager.domain.exceptions.errors import ConversionError
from file_manager.infrastructure.converters.markdown_table import build_markdown_table


class DocxToMarkdownConverter:
    """Converte arquivos .docx em Markdown."""

    supported_extensions = frozenset({".docx"})

    def convert(self, source: Path) -> str:
        try:
            document = Document(str(source))
        except Exception as error:
            # Arquivo corrompido ou que não é um DOCX de verdade.
            raise ConversionError(
                f"Não foi possível abrir o DOCX (arquivo corrompido?): {error}"
            ) from error

        output = ""
        previous_was_list = False

        # O corpo do documento mistura parágrafos (w:p) e tabelas (w:tbl).
        # Percorrer os elementos filhos nos dá tudo NA ORDEM em que aparece.
        for element in document.element.body.iterchildren():
            if element.tag == qn("w:p"):
                text, is_list = self._paragraph_to_markdown(Paragraph(element, document))
            elif element.tag == qn("w:tbl"):
                text, is_list = self._table_to_markdown(Table(element, document)), False
            else:
                continue  # outros elementos (ex.: configuração de página)

            if not text:
                continue

            # Itens de lista consecutivos ficam juntos (uma quebra de linha);
            # os demais blocos são separados por uma linha em branco.
            if output:
                output += "\n" if (is_list and previous_was_list) else "\n\n"
            output += text
            previous_was_list = is_list

        return output

    def _paragraph_to_markdown(self, paragraph: Paragraph) -> tuple[str, bool]:
        """Converte um parágrafo. Retorna (texto Markdown, é item de lista?)."""
        text = paragraph.text.strip()
        if not text:
            return "", False

        style_name = (paragraph.style.name if paragraph.style is not None else "") or ""
        style_lower = style_name.lower()

        heading_level = self._heading_level(style_lower)
        if heading_level:
            return f"{'#' * heading_level} {text}", False

        marker = self._list_marker(paragraph, style_lower)
        if marker is not None:
            indent = "  " * self._list_depth(paragraph, style_lower)
            return f"{indent}{marker} {text}", True

        return text, False

    @staticmethod
    def _heading_level(style_lower: str) -> int:
        """Nível do título (1 a 6) a partir do nome do estilo, ou 0 se não for título."""
        if style_lower == "title":
            return 1
        if style_lower.startswith("heading "):
            suffix = style_lower.removeprefix("heading ")
            if suffix.isdigit():
                return min(int(suffix), 6)  # Markdown só tem 6 níveis
        return 0

    @staticmethod
    def _has_numbering(paragraph: Paragraph) -> bool:
        """Verifica se o parágrafo tem formatação de lista aplicada diretamente."""
        # _p é o elemento XML interno do parágrafo; pPr guarda suas propriedades
        # e numPr indica que ele faz parte de uma lista.
        properties = paragraph._p.pPr
        return properties is not None and properties.numPr is not None

    def _list_marker(self, paragraph: Paragraph, style_lower: str) -> str | None:
        """Devolve o marcador da lista ('-' ou '1.') ou None se não for item de lista."""
        if style_lower.startswith("list number"):
            return "1."
        if style_lower.startswith("list bullet"):
            return "-"
        if self._has_numbering(paragraph):
            return "-"
        return None

    @staticmethod
    def _list_depth(paragraph: Paragraph, style_lower: str) -> int:
        """Nível de recuo do item (0 = primeiro nível)."""
        properties = paragraph._p.pPr
        if (
            properties is not None
            and properties.numPr is not None
            and properties.numPr.ilvl is not None
        ):
            return int(properties.numPr.ilvl.val)

        # Estilos como "List Bullet 2" indicam o nível no final do nome.
        last_word = style_lower.split()[-1] if style_lower else ""
        if last_word.isdigit() and int(last_word) > 1:
            return int(last_word) - 1
        return 0

    @staticmethod
    def _table_to_markdown(table: Table) -> str:
        """Converte uma tabela do Word em tabela Markdown."""
        rows = [[cell.text for cell in row.cells] for row in table.rows]
        return build_markdown_table(rows)