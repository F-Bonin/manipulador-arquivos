"""Interface de terminal para separar PDF (camada de APRESENTAÇÃO).

Uso (na raiz do projeto, com o .venv ativo):

    python -m file_manager.presentation.cli.split_cli "arquivo.pdf"
"""

from __future__ import annotations

import argparse
import sys

from file_manager.bootstrap import build_split_pdf_use_case
from file_manager.domain.exceptions.errors import FileManagerError
from file_manager.infrastructure.config.settings import load_settings
from file_manager.presentation.cli.cli_utils import resolve_source


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada. Retorna 0 em caso de sucesso e 1 em caso de erro."""
    parser = argparse.ArgumentParser(description="Separa um PDF em um arquivo por página.")
    parser.add_argument("arquivo", help="Caminho do PDF ou nome de um arquivo da pasta library.")
    args = parser.parse_args(argv)

    settings = load_settings()
    settings.ensure_directories()

    use_case = build_split_pdf_use_case(settings)
    source = resolve_source(args.arquivo, settings.library_dir)

    try:
        result = use_case.execute(source)
    except FileManagerError as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1

    print(f"PDF separado com sucesso: {result.total_pages} página(s).")
    print(f"Pasta de saída: {result.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())