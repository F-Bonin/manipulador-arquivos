"""Configurações da aplicação.

Este módulo pertence à camada de INFRAESTRUTURA: ele conhece detalhes
técnicos (arquivo .env, variáveis de ambiente, caminhos no disco) que as
camadas de domínio e aplicação não precisam saber.

Responsabilidade: ler as variáveis do arquivo .env e entregá-las ao restante
do programa em um único objeto organizado (Settings).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# __file__ é o caminho deste arquivo (settings.py). Subindo pelas pastas:
#   parents[0] -> config/
#   parents[1] -> infrastructure/
#   parents[2] -> file_manager/
#   parents[3] -> src/
#   parents[4] -> raiz do projeto (onde estão o .env e a pasta data/)
PROJECT_ROOT: Path = Path(__file__).resolve().parents[4]

# Carrega o arquivo .env da raiz do projeto para dentro das variáveis de
# ambiente do processo. Se o arquivo não existir, nada acontece e o
# programa usará os valores padrão definidos mais abaixo.
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    """Conjunto de configurações da aplicação.

    O parâmetro frozen=True torna o objeto imutável: depois de criado,
    ninguém altera uma configuração por engano durante a execução.
    """

    app_env: str          # Ambiente de execução: local, staging, production
    log_level: str        # Nível de detalhe dos logs
    max_upload_mb: int    # Tamanho máximo de upload, em megabytes
    large_output_warning_chars: int  # Acima disso, a conversão mostra um aviso de tamanho
    library_dir: Path     # Pasta com os arquivos que já estão no programa
    uploads_dir: Path     # Pasta onde ficam os arquivos novos enviados
    output_dir: Path      # Pasta onde ficam os resultados gerados

    def ensure_directories(self) -> None:
        """Cria as pastas de trabalho caso ainda não existam.

        parents=True cria também as pastas-pai que faltarem.
        exist_ok=True evita erro se a pasta já existir.
        """
        for directory in (self.library_dir, self.uploads_dir, self.output_dir):
            directory.mkdir(parents=True, exist_ok=True)


def _resolve_directory(env_name: str, default_relative: str) -> Path:
    """Converte uma variável de ambiente em um caminho absoluto.

    Args:
        env_name: nome da variável no .env (ex.: "UPLOADS_DIR").
        default_relative: valor usado se a variável não estiver definida.

    Returns:
        Caminho absoluto. Caminhos relativos são interpretados a partir
        da raiz do projeto, e não da pasta onde o terminal está aberto.
    """
    raw_value = os.getenv(env_name, default_relative)
    path = Path(raw_value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def load_settings() -> Settings:
    """Lê as variáveis de ambiente e monta o objeto Settings.

    Cada os.getenv("NOME", "padrão") busca a variável NOME; se ela não
    existir, usa o valor padrão informado.
    """
    return Settings(
        app_env=os.getenv("APP_ENV", "local"),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        # As variáveis de ambiente sempre chegam como texto, por isso int().
        max_upload_mb=int(os.getenv("MAX_UPLOAD_MB", "200")),
        large_output_warning_chars=int(os.getenv("LARGE_OUTPUT_WARNING_CHARS", "500000")),
        library_dir=_resolve_directory("LIBRARY_DIR", "data/library"),
        uploads_dir=_resolve_directory("UPLOADS_DIR", "data/uploads"),
        output_dir=_resolve_directory("OUTPUT_DIR", "data/output"),
    )