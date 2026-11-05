"""Conversor de planilhas (CSV, XLSX, XLS) para Markdown.

Camada de INFRAESTRUTURA.

Bibliotecas usadas:
  - csv (já vem com o Python)  -> arquivos .csv
  - pandas                     -> arquivos .xlsx e .xls
    (o pandas usa o openpyxl para .xlsx e o xlrd para .xls por baixo dos panos)

Este conversor cumpre dois contratos:
  - MarkdownConverter    -> converter o arquivo inteiro
  - SheetAwareConverter  -> listar abas e converter só algumas
"""

from __future__ import annotations

import csv
import io
import math
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from pathlib import Path

from file_manager.domain.exceptions.errors import ConversionError, FileManagerError
from file_manager.infrastructure.converters.markdown_table import build_markdown_table
from file_manager.infrastructure.converters.text_file_reader import read_text_file


@contextmanager
def _translate_errors() -> Iterator[None]:
    """Traduz erros técnicos das bibliotecas para erros do nosso domínio.

    Uso:
        with _translate_errors():
            ...código que pode falhar...
    """
    try:
        yield
    except FileManagerError:
        # Erros nossos já têm mensagem clara: apenas repassa.
        raise
    except Exception as error:
        raise ConversionError(f"Não foi possível ler a planilha: {error}") from error


class SpreadsheetToMarkdownConverter:
    """Converte planilhas em tabelas Markdown.

    - CSV: gera uma tabela.
    - XLSX/XLS: gera uma seção (## Nome da aba) com uma tabela para cada aba.
    """

    supported_extensions = frozenset({".csv", ".xlsx", ".xls"})

    # ------------------------------------------------------- API pública

    def convert(self, source: Path) -> str:
        """Converte o arquivo inteiro (todas as abas)."""
        with _translate_errors():
            if self._is_csv(source):
                return self._convert_csv(source)
            return self._convert_excel(source, sheet_names=None)

    def list_sheets(self, source: Path) -> list[str]:
        """Devolve os nomes das abas. CSV não tem abas, então devolve lista vazia."""
        with _translate_errors():
            if self._is_csv(source):
                return []

            # Import "tardio": o pandas é pesado e demora para carregar.
            import pandas as pd

            # ExcelFile abre o arquivo para consulta; o "with" garante que ele
            # será fechado ao final (no Windows, arquivo aberto fica travado).
            with pd.ExcelFile(source) as workbook:
                return [str(name) for name in workbook.sheet_names]

    def convert_sheets(self, source: Path, sheet_names: Sequence[str]) -> str:
        """Converte somente as abas indicadas."""
        with _translate_errors():
            if self._is_csv(source):
                raise ConversionError("Arquivos CSV não possuem abas para escolher.")

            available = self.list_sheets(source)
            chosen = self._resolve_sheet_names(sheet_names, available)
            return self._convert_excel(source, sheet_names=chosen)

    # ------------------------------------------------------------------ CSV

    @staticmethod
    def _is_csv(source: Path) -> bool:
        return source.suffix.lower() == ".csv"

    def _convert_csv(self, source: Path) -> str:
        """Lê um CSV detectando o separador (vírgula, ponto e vírgula etc.)."""
        text = read_text_file(source)

        # O Sniffer analisa uma amostra do texto para descobrir o separador.
        # No Brasil é comum usar ";" em vez de ",".
        try:
            dialect = csv.Sniffer().sniff(text[:4096], delimiters=",;\t|")
        except csv.Error:
            # Não deu para detectar (ex.: arquivo de uma coluna): usa vírgula.
            dialect = csv.excel

        # newline="" é a forma recomendada pelo Python para ler CSV de texto,
        # pois preserva quebras de linha que estejam dentro de células.
        reader = csv.reader(io.StringIO(text, newline=""), dialect)
        rows = [[cell.strip() for cell in row] for row in reader]
        return build_markdown_table(rows)

    # ---------------------------------------------------------------- Excel

    @staticmethod
    def _resolve_sheet_names(requested: Sequence[str], available: list[str]) -> list[str]:
        """Converte os nomes digitados nos nomes reais das abas.

        A comparação ignora maiúsculas/minúsculas e espaços nas pontas,
        então "resumo" encontra a aba "Resumo".
        """
        # casefold() é uma versão mais completa do lower(), própria para comparar texto.
        lookup = {name.casefold(): name for name in available}

        resolved: list[str] = []
        missing: list[str] = []
        for name in requested:
            actual = lookup.get(name.strip().casefold())
            if actual is None:
                missing.append(name)
            elif actual not in resolved:  # evita repetir a mesma aba
                resolved.append(actual)

        if missing:
            raise ConversionError(
                f"Aba(s) não encontrada(s): {', '.join(missing)}. "
                f"Abas disponíveis: {', '.join(available)}."
            )
        return resolved

    def _convert_excel(self, source: Path, sheet_names: list[str] | None) -> str:
        """Lê abas de um arquivo Excel (.xlsx ou .xls) com o pandas.

        Args:
            source: arquivo Excel.
            sheet_names: abas a ler; None significa TODAS as abas.
        """
        import pandas as pd

        sheets = pd.read_excel(
            source,
            sheet_name=sheet_names,  # None = todas; lista = só as indicadas
            header=None,             # não tratar a 1ª linha como cabeçalho: nós montamos
            dtype=str,               # tudo como texto, evitando 1 virar 1.0
            keep_default_na=False,   # células vazias ficam como texto vazio
        )

        blocks: list[str] = []
        for sheet_name, frame in sheets.items():
            # itertuples(index=False, name=None) devolve cada linha como tupla simples.
            rows = [
                self._trim_trailing_empty([self._cell_to_text(value) for value in row])
                for row in frame.itertuples(index=False, name=None)
            ]
            table = build_markdown_table(rows)
            if table:  # abas vazias são ignoradas
                blocks.append(f"## {sheet_name}\n\n{table}")

        return "\n\n".join(blocks)

    # ------------------------------------------------------------- Auxiliares

    @staticmethod
    def _trim_trailing_empty(row: list[str]) -> list[str]:
        """Remove as células vazias do final da linha (colunas "fantasmas")."""
        while row and row[-1] == "":
            row.pop()
        return row

    @staticmethod
    def _cell_to_text(value: object) -> str:
        """Converte o valor de uma célula em texto limpo."""
        if value is None:
            return ""
        # Células vazias podem chegar como NaN (um float "não é número").
        if isinstance(value, float) and math.isnan(value):
            return ""

        text = str(value).strip()

        # Datas lidas como texto vêm com a hora: "2026-11-05 00:00:00".
        # Quando a hora é meia-noite, mostramos só a data.
        midnight = " 00:00:00"
        if text.endswith(midnight):
            text = text[: -len(midnight)]
        return text