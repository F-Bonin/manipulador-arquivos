"""Caso de uso: converter um arquivo para Markdown (camada de APLICAÇÃO).

O caso de uso escolhe o conversor certo pela extensão do arquivo, executa
a conversão e grava o resultado em um arquivo .md.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

from file_manager.application.interfaces.markdown_converter import (
    MarkdownConverter,
    SheetAwareConverter,
)
from file_manager.domain.entities.conversion_result import ConversionResult
from file_manager.domain.exceptions.errors import (
    ConversionError,
    InvalidFileError,
    UnsupportedFormatError,
)

# Limite padrão (em caracteres) a partir do qual mostramos um aviso de tamanho.
_DEFAULT_LARGE_OUTPUT_CHARS = 500_000


class ConvertToMarkdownUseCase:
    """Converte PDF, DOCX, planilhas e TXT em um arquivo Markdown."""

    def __init__(
        self,
        converters: Sequence[MarkdownConverter],
        output_dir: Path,
        large_output_chars: int = _DEFAULT_LARGE_OUTPUT_CHARS,
    ) -> None:
        """Recebe as dependências já prontas (injeção de dependência).

        Args:
            converters: conversores disponíveis (um por formato).
            output_dir: pasta onde os arquivos .md serão gravados.
            large_output_chars: acima desta quantidade de caracteres, o
                resultado inclui um aviso de tamanho.
        """
        self._converters = tuple(converters)
        self._output_dir = output_dir
        self._large_output_chars = large_output_chars

    @property
    def supported_extensions(self) -> frozenset[str]:
        """Todas as extensões aceitas, somando as de cada conversor."""
        return frozenset().union(*(c.supported_extensions for c in self._converters))

    def list_sheets(self, source: Path) -> list[str]:
        """Lista os nomes das abas de uma planilha.

        Raises:
            InvalidFileError: se o arquivo não existir.
            UnsupportedFormatError: se não houver conversor para a extensão.
            ConversionError: se o formato não tiver abas (PDF, DOCX, TXT).
        """
        self._ensure_file_exists(source)
        converter = self._find_converter(source)
        return self._require_sheet_support(converter, source).list_sheets(source)

    def execute(
        self,
        source: Path,
        sheet_names: Sequence[str] | None = None,
    ) -> ConversionResult:
        """Executa a conversão.

        Args:
            source: caminho do arquivo a converter.
            sheet_names: se informado, converte somente estas abas (apenas
                para planilhas). Se None, converte o arquivo inteiro.

        Raises:
            InvalidFileError: se o arquivo não existir.
            UnsupportedFormatError: se não houver conversor para a extensão.
            ConversionError: se a conversão falhar ou não gerar nenhum texto.
        """
        self._ensure_file_exists(source)
        converter = self._find_converter(source)

        if sheet_names:
            sheet_converter = self._require_sheet_support(converter, source)
            markdown = sheet_converter.convert_sheets(source, sheet_names)
        else:
            markdown = converter.convert(source)

        # Conteúdo vazio costuma indicar um PDF escaneado (só imagem).
        if not markdown.strip():
            raise ConversionError(
                "Nenhum texto foi encontrado no arquivo. Se for um PDF escaneado "
                "(imagem), ele precisará de OCR, que será implementado em uma fase futura."
            )

        # parents=True cria pastas-pai que faltarem; exist_ok=True evita erro
        # se a pasta já existir.
        self._output_dir.mkdir(parents=True, exist_ok=True)
        destination = self._build_destination(source)
        destination.write_text(markdown, encoding="utf-8")

        return ConversionResult(
            source_file=source,
            output_file=destination,
            character_count=len(markdown),
            warnings=self._build_warnings(len(markdown), converter, source, sheet_names),
        )

    @staticmethod
    def _ensure_file_exists(source: Path) -> None:
        """Garante que o caminho aponta para um arquivo existente."""
        if not source.is_file():
            raise InvalidFileError(f"Arquivo não encontrado: {source}")

    def _find_converter(self, source: Path) -> MarkdownConverter:
        """Escolhe o conversor cuja lista de extensões contém a do arquivo."""
        extension = source.suffix.lower()  # lower() aceita ".PDF" e ".pdf"
        for converter in self._converters:
            if extension in converter.supported_extensions:
                return converter

        accepted = ", ".join(sorted(self.supported_extensions))
        raise UnsupportedFormatError(
            f"Formato '{extension}' não suportado. Formatos aceitos: {accepted}"
        )

    @staticmethod
    def _require_sheet_support(
        converter: MarkdownConverter, source: Path
    ) -> SheetAwareConverter:
        """Garante que o conversor entende abas (só planilhas entendem)."""
        if not isinstance(converter, SheetAwareConverter):
            raise ConversionError(
                f"Arquivos '{source.suffix.lower()}' não possuem abas para escolher."
            )
        return converter

    def _build_warnings(
        self,
        character_count: int,
        converter: MarkdownConverter,
        source: Path,
        sheet_names: Sequence[str] | None,
    ) -> tuple[str, ...]:
        """Monta os avisos para o usuário, se houver."""
        if character_count <= self._large_output_chars:
            return ()

        # Troca a vírgula do separador de milhar por ponto (padrão brasileiro).
        formatted = f"{character_count:,}".replace(",", ".")
        recommendation = self._build_recommendation(converter, source, sheet_names)
        return (
            f"O arquivo gerado é grande ({formatted} caracteres) e pode ser pesado "
            f"para abrir ou colar em outras ferramentas. {recommendation}",
        )

    @staticmethod
    def _build_recommendation(
        converter: MarkdownConverter,
        source: Path,
        sheet_names: Sequence[str] | None,
    ) -> str:
        """Escolhe a recomendação certa para o tipo de arquivo convertido."""
        # Só faz sentido recomendar "uma aba por vez" para conversores que
        # entendem abas (planilhas) e quando há mais de uma aba envolvida.
        if isinstance(converter, SheetAwareConverter):
            # Se o usuário escolheu abas, conta as escolhidas; senão, conta
            # todas as abas do arquivo.
            total_sheets = len(sheet_names) if sheet_names else len(converter.list_sheets(source))
            if total_sheets > 1:
                return "Recomendação: converta uma aba por vez!"

        return "Recomendação: divida o arquivo original em partes menores e converta uma parte por vez."

    def _build_destination(self, source: Path) -> Path:
        """Define o nome do arquivo .md, com data e hora para não sobrescrever."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self._output_dir / f"{source.stem}_{timestamp}.md"