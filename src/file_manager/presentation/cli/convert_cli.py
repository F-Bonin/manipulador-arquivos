"""Interface de terminal para converter arquivos em Markdown.

Camada de APRESENTAÇÃO.

Exemplos de uso (na raiz do projeto, com o .venv ativo):

    # Converter um arquivo (PDF, DOCX, XLSX, XLS, CSV ou TXT)
    python -m file_manager.presentation.cli.convert_cli "arquivo.docx"

    # Ver os nomes das abas de uma planilha
    python -m file_manager.presentation.cli.convert_cli "planilha.xlsx" --listar-abas

    # Converter só algumas abas (repita --aba para cada uma)
    python -m file_manager.presentation.cli.convert_cli "planilha.xlsx" --aba "Janeiro" --aba "Fevereiro"
"""

from __future__ import annotations

import argparse
import sys

from file_manager.bootstrap import build_convert_to_markdown_use_case
from file_manager.domain.exceptions.errors import FileManagerError
from file_manager.infrastructure.config.settings import load_settings
from file_manager.presentation.cli.cli_utils import resolve_source


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada. Retorna 0 em caso de sucesso e 1 em caso de erro."""
    parser = argparse.ArgumentParser(
        description="Converte PDF, DOCX, planilhas (XLSX, XLS, CSV) e TXT em Markdown."
    )
    parser.add_argument(
        "arquivo", help="Caminho do arquivo ou nome de um arquivo da pasta library."
    )
    parser.add_argument(
        "--listar-abas",
        action="store_true",  # vira True se a opção for usada
        help="Mostra os nomes das abas da planilha e termina (não converte).",
    )
    parser.add_argument(
        "--aba",
        action="append",  # permite repetir a opção; os valores formam uma lista
        metavar="NOME",
        help="Converte somente esta aba. Repita a opção para escolher várias.",
    )
    args = parser.parse_args(argv)

    settings = load_settings()
    settings.ensure_directories()

    use_case = build_convert_to_markdown_use_case(settings)
    source = resolve_source(args.arquivo, settings.library_dir)

    try:
        if args.listar_abas:
            sheets = use_case.list_sheets(source)
            if not sheets:
                print("Este arquivo não possui abas.")
                return 0
            print(f"{len(sheets)} aba(s) encontrada(s):")
            for number, name in enumerate(sheets, start=1):
                print(f"  {number}. {name}")
            return 0

        result = use_case.execute(source, sheet_names=args.aba)
    except FileManagerError as error:
        # Erros previstos do programa viram uma mensagem amigável.
        print(f"Erro: {error}", file=sys.stderr)
        return 1

    print(f"Conversão concluída: {result.character_count} caracteres.")
    print(f"Arquivo gerado: {result.output_file}")
    for warning in result.warnings:
        print(f"Aviso: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())