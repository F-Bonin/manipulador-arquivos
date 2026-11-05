"""Leitura de arquivos de texto com detecção simples de codificação.

Arquivos de texto criados no Windows nem sempre usam UTF-8. Se lermos com a
codificação errada, letras acentuadas viram símbolos estranhos. Por isso
tentamos algumas codificações, da mais provável para a menos provável.
"""

from __future__ import annotations

from pathlib import Path

# Ordem de tentativa:
#   utf-8-sig -> UTF-8 (com ou sem BOM, marca que alguns editores adicionam)
#   cp1252    -> padrão do Windows em português
#   latin-1   -> aceita qualquer sequência de bytes (último recurso)
_ENCODINGS = ("utf-8-sig", "cp1252", "latin-1")


def read_text_file(path: Path) -> str:
    """Lê um arquivo de texto, testando as codificações em sequência."""
    raw = path.read_bytes()
    for encoding in _ENCODINGS:
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            # Esta codificação não serve para o arquivo: tenta a próxima.
            continue

    # Não deve ser alcançado, pois latin-1 decodifica qualquer byte.
    return raw.decode("latin-1", errors="replace")