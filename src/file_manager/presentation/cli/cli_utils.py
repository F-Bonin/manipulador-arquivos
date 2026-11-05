"""Funções compartilhadas pelos comandos de terminal (camada de APRESENTAÇÃO)."""

from __future__ import annotations

from pathlib import Path


def resolve_source(raw_path: str, library_dir: Path) -> Path:
    """Descobre qual arquivo o usuário quis dizer.

    Ordem de busca:
      1. O caminho exatamente como foi digitado.
      2. Um arquivo com esse nome dentro da pasta library
         (arquivos que já estão dentro do programa).
    """
    candidate = Path(raw_path).expanduser()
    if candidate.is_file():
        return candidate

    in_library = library_dir / raw_path
    if in_library.is_file():
        return in_library

    # Não achou: devolve o caminho original e o caso de uso informará o erro.
    return candidate