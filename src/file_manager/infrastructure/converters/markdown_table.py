"""Montagem de tabelas em Markdown (camada de INFRAESTRUTURA).

Tanto as planilhas quanto as tabelas do DOCX viram tabelas Markdown.
Este módulo reúne essa lógica em um só lugar, para não repeti-la.

Formato gerado:

    | Coluna A | Coluna B |
    | --- | --- |
    | valor 1 | valor 2 |
"""

from __future__ import annotations

from collections.abc import Sequence


def _escape_cell(text: str) -> str:
    """Prepara o texto de uma célula para caber em uma tabela Markdown.

    - O caractere "|" separa colunas, então é "escapado" com barra invertida.
    - Quebras de linha quebrariam a tabela, então viram <br>.
    """
    cleaned = text.strip()
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")
    return cleaned.replace("|", "\\|")


def _format_row(cells: Sequence[str]) -> str:
    """Junta as células de uma linha no formato '| a | b |'."""
    return "| " + " | ".join(cells) + " |"


def build_markdown_table(rows: Sequence[Sequence[str]]) -> str:
    """Converte linhas de texto em uma tabela Markdown.

    A PRIMEIRA linha é usada como cabeçalho da tabela.

    Args:
        rows: lista de linhas; cada linha é uma lista de textos (células).

    Returns:
        A tabela em Markdown, ou texto vazio se não houver nenhum conteúdo.
    """
    # Descarta linhas em que todas as células estão vazias.
    non_empty_rows = [row for row in rows if any(cell.strip() for cell in row)]
    if not non_empty_rows:
        return ""

    # Algumas linhas podem ter menos células que outras (arquivos irregulares).
    # Completamos com células vazias para todas terem a mesma largura.
    width = max(len(row) for row in non_empty_rows)
    normalized = [
        [_escape_cell(cell) for cell in row] + [""] * (width - len(row))
        for row in non_empty_rows
    ]

    # "header, *body" separa a primeira linha (cabeçalho) das demais.
    header, *body = normalized
    lines = [_format_row(header), _format_row(["---"] * width)]
    lines.extend(_format_row(row) for row in body)
    return "\n".join(lines)