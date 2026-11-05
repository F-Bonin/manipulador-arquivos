"""Testes da montagem de tabelas Markdown."""

from file_manager.infrastructure.converters.markdown_table import build_markdown_table


def test_builds_table_using_first_row_as_header():
    rows = [["Nome", "Idade"], ["Ana", "30"]]

    assert build_markdown_table(rows) == (
        "| Nome | Idade |\n"
        "| --- | --- |\n"
        "| Ana | 30 |"
    )


def test_escapes_pipe_and_replaces_line_breaks():
    rows = [["Texto"], ["a|b"], ["linha 1\nlinha 2"]]

    table = build_markdown_table(rows)

    assert "| a\\|b |" in table
    assert "| linha 1<br>linha 2 |" in table


def test_pads_short_rows_with_empty_cells():
    rows = [["A", "B", "C"], ["1"]]

    assert build_markdown_table(rows).splitlines()[-1] == "| 1 |  |  |"


def test_returns_empty_text_when_there_is_no_content():
    assert build_markdown_table([]) == ""
    assert build_markdown_table([["", " "], [""]]) == ""


def test_skips_completely_blank_rows():
    rows = [["A", "B"], ["", ""], ["1", "2"]]

    lines = build_markdown_table(rows).splitlines()

    assert len(lines) == 3  # cabeçalho + separador + 1 linha de dados