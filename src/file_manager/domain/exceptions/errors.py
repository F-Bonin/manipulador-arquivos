"""Erros do negócio (camada de DOMÍNIO).

Criar erros próprios, em vez de usar apenas os erros genéricos do Python,
permite que cada camada reconheça exatamente o que deu errado e mostre uma
mensagem clara ao usuário.

Hierarquia:

    FileManagerError            <- erro "pai": captura qualquer erro do programa
     ├── InvalidFileError       <- arquivo inexistente ou de tipo errado
     ├── CorruptedPdfError      <- PDF danificado ou ilegível
     └── EncryptedPdfError      <- PDF protegido por senha
"""


class FileManagerError(Exception):
    """Erro base de todo o programa.

    Quem quiser tratar qualquer erro previsto do sistema pode usar
    `except FileManagerError`, sem listar um por um.
    """


class InvalidFileError(FileManagerError):
    """O arquivo informado não existe ou não é do tipo esperado."""


class CorruptedPdfError(FileManagerError):
    """O PDF está corrompido, vazio ou não pôde ser lido."""


class EncryptedPdfError(FileManagerError):
    """O PDF está protegido por senha e não pôde ser aberto."""