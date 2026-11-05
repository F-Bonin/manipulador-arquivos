"""Testes de integração dos conversores.

Cada teste cria um arquivo real e temporário, converte e confere o Markdown.
"""

from pathlib import Path

import pandas as pd
import pymupdf
import pytest
from docx import Document

from file_manager.domain.exceptions.errors import ConversionError
from file_manager.infrastructure.converters.docx_converter import DocxToMarkdownConverter
from file_manager.infrastructure.converters.pdf_converter import PdfToMarkdownConverter
from file_manager.infrastructure.converters.spreadsheet_converter import (
    SpreadsheetToMarkdownConverter,
)
from file_manager.infrastructure.converters.text_converter import TextToMarkdownConverter


def test_text_converter_handles_windows_encoding(tmp_path: Path):
    """Um TXT salvo em cp1252 (padrão do Windows) mantém os acentos."""
    source = tmp_path / "texto.txt"
    source.write_bytes("Ação e emoção".encode("cp1252"))

    assert TextToMarkdownConverter().convert(source) == "Ação e emoção"


def test_csv_with_semicolon_becomes_markdown_table(tmp_path: Path):
    """Um CSV separado por ponto e vírgula vira uma tabela Markdown."""
    source = tmp_path / "pessoas.csv"
    source.write_text("Nome;Idade\nAna;30\nBruno;25\nCarla;41\n", encoding="utf-8")

    markdown = SpreadsheetToMarkdownConverter().convert(source)

    assert "| Nome | Idade |" in markdown
    assert "| Ana | 30 |" in markdown
    assert "| Carla | 41 |" in markdown


def test_excel_becomes_markdown_with_sheet_name(tmp_path: Path):
    """Cada aba do Excel vira uma seção com o nome da aba."""
    source = tmp_path / "vendas.xlsx"
    frame = pd.DataFrame({"Produto": ["Caneta", "Lápis"], "Quantidade": [10, 5]})
    frame.to_excel(source, index=False, sheet_name="Vendas")

    markdown = SpreadsheetToMarkdownConverter().convert(source)

    assert "## Vendas" in markdown
    assert "| Produto | Quantidade |" in markdown
    assert "| Caneta | 10 |" in markdown


def test_docx_converts_heading_paragraph_list_and_table(tmp_path: Path):
    """Título, parágrafo, lista e tabela são convertidos na ordem do documento."""
    source = tmp_path / "documento.docx"
    document = Document()
    document.add_heading("Título Principal", level=1)
    document.add_paragraph("Um parágrafo normal.")
    document.add_paragraph("Item um", style="List Bullet")
    document.add_paragraph("Item dois", style="List Bullet")
    table = document.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Nome"
    table.cell(0, 1).text = "Idade"
    table.cell(1, 0).text = "Ana"
    table.cell(1, 1).text = "30"
    document.save(str(source))

    markdown = DocxToMarkdownConverter().convert(source)

    assert "# Título Principal" in markdown
    assert "Um parágrafo normal." in markdown
    assert "- Item um\n- Item dois" in markdown
    assert "| Nome | Idade |" in markdown
    assert "| Ana | 30 |" in markdown


def test_docx_raises_conversion_error_for_invalid_file(tmp_path: Path):
    """Um arquivo .docx que não é um DOCX de verdade gera ConversionError."""
    source = tmp_path / "quebrado.docx"
    source.write_bytes(b"isto nao e um docx")

    with pytest.raises(ConversionError):
        DocxToMarkdownConverter().convert(source)


def test_pdf_with_text_is_converted(tmp_path: Path):
    """O texto de um PDF com texto selecionável aparece no Markdown."""
    source = tmp_path / "texto.pdf"
    pdf = pymupdf.open()          # cria um PDF vazio
    page = pdf.new_page()         # adiciona uma página
    page.insert_text((72, 72), "Hello PDF World")
    pdf.save(str(source))
    pdf.close()

    markdown = PdfToMarkdownConverter().convert(source)

    assert "Hello PDF World" in markdown

def _create_two_sheet_workbook(path: Path) -> None:
    """Cria uma planilha de teste com duas abas: Resumo e Detalhes."""
    with pd.ExcelWriter(path) as writer:
        pd.DataFrame({"Total": [100]}).to_excel(writer, sheet_name="Resumo", index=False)
        pd.DataFrame({"Item": ["A"]}).to_excel(writer, sheet_name="Detalhes", index=False)


def test_excel_list_sheets_returns_all_names(tmp_path: Path):
    source = tmp_path / "relatorio.xlsx"
    _create_two_sheet_workbook(source)

    assert SpreadsheetToMarkdownConverter().list_sheets(source) == ["Resumo", "Detalhes"]


def test_excel_convert_sheets_returns_only_selected_sheet(tmp_path: Path):
    """Só a aba pedida aparece, e o nome é aceito em minúsculas."""
    source = tmp_path / "relatorio.xlsx"
    _create_two_sheet_workbook(source)

    markdown = SpreadsheetToMarkdownConverter().convert_sheets(source, ["resumo"])

    assert "## Resumo" in markdown
    assert "## Detalhes" not in markdown


def test_excel_convert_sheets_raises_for_unknown_sheet(tmp_path: Path):
    source = tmp_path / "relatorio.xlsx"
    _create_two_sheet_workbook(source)

    with pytest.raises(ConversionError):
        SpreadsheetToMarkdownConverter().convert_sheets(source, ["Inexistente"])