"""Testes unitários do caso de uso ConvertToMarkdownUseCase.

Usamos um conversor FALSO, para testar apenas a regra do caso de uso
(escolha do conversor, validações e gravação do arquivo).
"""

from pathlib import Path

import pytest

from file_manager.application.use_cases.convert_to_markdown import ConvertToMarkdownUseCase
from file_manager.domain.exceptions.errors import (
    ConversionError,
    InvalidFileError,
    UnsupportedFormatError,
)


class FakeConverter:
    """Conversor falso: devolve sempre o Markdown informado."""

    supported_extensions = frozenset({".txt"})

    def __init__(self, markdown: str = "# Olá") -> None:
        self._markdown = markdown

    def convert(self, source: Path) -> str:
        return self._markdown


def test_execute_writes_markdown_file(tmp_path: Path):
    source = tmp_path / "nota.txt"
    source.write_text("conteudo")
    output_dir = tmp_path / "saida"

    result = ConvertToMarkdownUseCase([FakeConverter("# Olá")], output_dir).execute(source)

    assert result.output_file.parent == output_dir
    assert result.output_file.suffix == ".md"
    assert result.output_file.name.startswith("nota_")
    assert result.output_file.read_text(encoding="utf-8") == "# Olá"
    assert result.character_count == len("# Olá")


def test_execute_accepts_uppercase_extension(tmp_path: Path):
    source = tmp_path / "NOTA.TXT"
    source.write_text("conteudo")

    result = ConvertToMarkdownUseCase([FakeConverter()], tmp_path / "saida").execute(source)

    assert result.output_file.exists()


def test_execute_raises_for_unsupported_format(tmp_path: Path):
    source = tmp_path / "dados.xyz"
    source.write_text("conteudo")

    with pytest.raises(UnsupportedFormatError):
        ConvertToMarkdownUseCase([FakeConverter()], tmp_path / "saida").execute(source)


def test_execute_raises_when_file_does_not_exist(tmp_path: Path):
    use_case = ConvertToMarkdownUseCase([FakeConverter()], tmp_path / "saida")

    with pytest.raises(InvalidFileError):
        use_case.execute(tmp_path / "nao_existe.txt")


def test_execute_raises_when_converter_returns_empty_text(tmp_path: Path):
    source = tmp_path / "vazio.txt"
    source.write_text("conteudo")

    with pytest.raises(ConversionError):
        ConvertToMarkdownUseCase([FakeConverter("   ")], tmp_path / "saida").execute(source)

class FakeSheetConverter:
    """Conversor falso de planilhas: tem abas e registra o que foi pedido."""

    supported_extensions = frozenset({".xlsx"})

    def __init__(self) -> None:
        self.requested_sheets: list[str] | None = None

    def convert(self, source: Path) -> str:
        return "# todas as abas"

    def list_sheets(self, source: Path) -> list[str]:
        return ["Resumo", "Detalhes"]

    def convert_sheets(self, source: Path, sheet_names) -> str:
        self.requested_sheets = list(sheet_names)
        return "# somente abas escolhidas"


def test_execute_adds_warning_when_output_is_large(tmp_path: Path):
    source = tmp_path / "grande.txt"
    source.write_text("conteudo")
    use_case = ConvertToMarkdownUseCase(
        [FakeConverter("a" * 50)], tmp_path / "saida", large_output_chars=10
    )

    result = use_case.execute(source)

    assert len(result.warnings) == 1
    assert "50" in result.warnings[0]


def test_execute_has_no_warning_when_output_is_small(tmp_path: Path):
    source = tmp_path / "pequeno.txt"
    source.write_text("conteudo")
    use_case = ConvertToMarkdownUseCase(
        [FakeConverter("a" * 50)], tmp_path / "saida", large_output_chars=1000
    )

    assert use_case.execute(source).warnings == ()


def test_execute_converts_only_selected_sheets(tmp_path: Path):
    source = tmp_path / "dados.xlsx"
    source.write_text("conteudo")
    converter = FakeSheetConverter()

    result = ConvertToMarkdownUseCase([converter], tmp_path / "saida").execute(
        source, sheet_names=["Resumo"]
    )

    assert converter.requested_sheets == ["Resumo"]
    assert result.output_file.read_text(encoding="utf-8") == "# somente abas escolhidas"


def test_execute_raises_when_selecting_sheets_on_format_without_sheets(tmp_path: Path):
    source = tmp_path / "nota.txt"
    source.write_text("conteudo")
    use_case = ConvertToMarkdownUseCase([FakeConverter()], tmp_path / "saida")

    with pytest.raises(ConversionError):
        use_case.execute(source, sheet_names=["Resumo"])


def test_list_sheets_returns_sheet_names(tmp_path: Path):
    source = tmp_path / "dados.xlsx"
    source.write_text("conteudo")
    use_case = ConvertToMarkdownUseCase([FakeSheetConverter()], tmp_path / "saida")

    assert use_case.list_sheets(source) == ["Resumo", "Detalhes"]
    
def test_warning_recommends_splitting_file_for_formats_without_sheets(tmp_path: Path):
    """Em um TXT grande, o aviso não fala em abas."""
    source = tmp_path / "grande.txt"
    source.write_text("conteudo")
    use_case = ConvertToMarkdownUseCase(
        [FakeConverter("a" * 50)], tmp_path / "saida", large_output_chars=10
    )

    warning = use_case.execute(source).warnings[0]

    assert "divida o arquivo original" in warning
    assert "uma aba por vez" not in warning


def test_warning_recommends_one_sheet_at_a_time_for_multi_sheet_workbook(tmp_path: Path):
    """Em uma planilha com várias abas, o aviso recomenda uma aba por vez."""
    source = tmp_path / "dados.xlsx"
    source.write_text("conteudo")
    use_case = ConvertToMarkdownUseCase(
        [FakeSheetConverter()], tmp_path / "saida", large_output_chars=5
    )

    warning = use_case.execute(source).warnings[0]

    assert "uma aba por vez" in warning


def test_warning_uses_generic_recommendation_when_only_one_sheet_selected(tmp_path: Path):
    """Com uma única aba escolhida, "uma aba por vez" não ajudaria."""
    source = tmp_path / "dados.xlsx"
    source.write_text("conteudo")
    use_case = ConvertToMarkdownUseCase(
        [FakeSheetConverter()], tmp_path / "saida", large_output_chars=5
    )

    warning = use_case.execute(source, sheet_names=["Resumo"]).warnings[0]

    assert "divida o arquivo original" in warning
    assert "uma aba por vez" not in warning