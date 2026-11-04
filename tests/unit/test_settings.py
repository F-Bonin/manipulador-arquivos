"""Testes das configurações da aplicação.

Servem para confirmar que a estrutura do projeto está correta: se o import
funciona e se as configurações são carregadas com valores coerentes.
"""

from file_manager.infrastructure.config.settings import PROJECT_ROOT, load_settings


def test_project_root_contains_src_folder():
    """A raiz calculada deve ser a pasta que contém 'src'."""
    assert (PROJECT_ROOT / "src").is_dir()


def test_load_settings_returns_expected_directories():
    """As pastas de trabalho devem ter os nomes esperados."""
    settings = load_settings()

    assert settings.library_dir.name == "library"
    assert settings.uploads_dir.name == "uploads"
    assert settings.output_dir.name == "output"


def test_load_settings_has_valid_upload_limit():
    """O limite de upload deve ser um número inteiro positivo."""
    settings = load_settings()

    assert isinstance(settings.max_upload_mb, int)
    assert settings.max_upload_mb > 0