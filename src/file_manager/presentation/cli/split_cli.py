"""Interface de terminal para separar PDF (camada de APRESENTAÇÃO).

Uso (na raiz do projeto, com o .venv ativo):

    python -m file_manager.presentation.cli.split_cli "C:\\caminho\\arquivo.pdf"
    python -m file_manager.presentation.cli.split_cli arquivo.pdf

Se o argumento não for um caminho existente, o programa procura o arquivo
na pasta data/library (arquivos que já estão dentro do programa).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from file_manager.bootstrap import build_split_pdf_use_case
from file_manager.domain.exceptions.errors import FileManagerError
from file_manager.infrastructure.config.settings import load_settings


def _resolve_source(raw_path: str, library_dir: Path) -> Path:
    """Descobre qual arquivo o usuário quis dizer.

    Ordem de busca:
      1. O caminho exatamente como foi digitado.
      2. Um arquivo com esse nome dentro da pasta library.
    """
    candidate = Path(raw_path).expanduser()
    if candidate.is_file():
        return candidate

    in_library = library_dir / raw_path
    if in_library.is_file():
        return in_library

    # Não achou: devolve o caminho original e o caso de uso informará o erro.
    return candidate


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada. Retorna 0 em caso de sucesso e 1 em caso de erro."""
    parser = argparse.ArgumentParser(description="Separa um PDF em um arquivo por página.")
    parser.add_argument("arquivo", help="Caminho do PDF ou nome de um arquivo da pasta library.")
    args = parser.parse_args(argv)

    settings = load_settings()
    settings.ensure_directories()

    use_case = build_split_pdf_use_case(settings)
    source = _resolve_source(args.arquivo, settings.library_dir)

    try:
        result = use_case.execute(source)
    except FileManagerError as error:
        # Erros previstos do programa viram uma mensagem amigável.
        print(f"Erro: {error}", file=sys.stderr)
        return 1

    print(f"PDF separado com sucesso: {result.total_pages} página(s).")
    print(f"Pasta de saída: {result.output_dir}")
    return 0


if __name__ == "__main__":
    # Só executa quando o arquivo é rodado diretamente (e não importado).
    raise SystemExit(main())