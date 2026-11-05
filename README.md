# Manipulador de Arquivos

Programa em Python para manipular arquivos, rodando localmente. Foi construído com **Clean Architecture** para crescer com segurança, e a interface web (Streamlit) está planejada para as próximas fases.

## Funcionalidades

**Disponíveis (pelo terminal):**

- Separar um PDF em um arquivo por página, mantendo a paginação original
- Converter para Markdown: PDF (com texto selecionável), DOCX, planilhas (XLSX, XLS, CSV) e TXT
- Em planilhas com várias abas: listar as abas e converter só as escolhidas
- Aviso automático quando o arquivo gerado é muito grande
- Trabalhar com arquivos já existentes no programa (`data/library`) ou com novos arquivos informados pelo caminho

**Planejadas:**

- OCR para PDFs escaneados
- Mesclar vários arquivos (PDF, DOCX, planilhas, TXT) em um único PDF
- Interface web com Streamlit

## Requisitos

- Windows
- Python 3.12
- VS Code (recomendado)

## Instalação

```powershell
git clone <URL-DO-REPOSITORIO>
cd manipulador-arquivos
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
copy .env.example .env
```

> **Windows com Controle Inteligente de Aplicativos:** algumas versões de bibliotecas
> (como o pandas 3.x) são bloqueadas. As versões deste projeto estão fixadas no
> `requirements.txt`. Para reproduzir exatamente o ambiente testado, use:
> `python -m pip install -r requirements.lock.txt`

## Configuração

As configurações ficam no arquivo `.env` (copiado de `.env.example`). O `.env` não é enviado ao Git.

| Variável | Para que serve | Padrão |
|---|---|---|
| `APP_ENV` | Ambiente de execução | `local` |
| `LOG_LEVEL` | Nível de detalhe dos logs | `INFO` |
| `MAX_UPLOAD_MB` | Tamanho máximo de upload, em MB | `200` |
| `LIBRARY_DIR` | Pasta dos arquivos que já estão no programa | `data/library` |
| `UPLOADS_DIR` | Pasta dos arquivos enviados | `data/uploads` |
| `OUTPUT_DIR` | Pasta dos resultados gerados | `data/output` |
| `LARGE_OUTPUT_WARNING_CHARS` | Acima desta quantidade de caracteres, a conversão mostra um aviso de tamanho | `500000` |

## Uso pelo terminal

Uso temporário, até a interface Streamlit ficar pronta. Execute na raiz do projeto, com o `.venv` ativo.

Se o argumento não for um caminho existente, o programa procura o arquivo na pasta `data/library`. Nomes com espaço precisam estar entre aspas.

```powershell
# Separar um PDF em uma página por arquivo
python -m file_manager.presentation.cli.split_cli "arquivo.pdf"

# Converter PDF, DOCX, XLSX, XLS, CSV ou TXT para Markdown
python -m file_manager.presentation.cli.convert_cli "arquivo.docx"

# Planilhas grandes: listar as abas e converter só algumas
python -m file_manager.presentation.cli.convert_cli "planilha.xlsx" --listar-abas
python -m file_manager.presentation.cli.convert_cli "planilha.xlsx" --aba "Janeiro" --aba "Fevereiro"
```

Os resultados são gravados em `data/output`.

## Testes

```powershell
python -m pytest -v
```

## Arquitetura

Clean Architecture em quatro camadas. As camadas internas nunca dependem das externas:

| Camada | Responsabilidade |
|---|---|
| `domain` | Entidades e erros do negócio (Python puro) |
| `application` | Casos de uso e contratos (interfaces) |
| `infrastructure` | Bibliotecas, disco e configuração |
| `presentation` | Terminal e, no futuro, a interface Streamlit |

Para suportar um novo formato de arquivo, crie um conversor que cumpra o contrato `MarkdownConverter` e registre-o em `bootstrap.py`.

```
manipulador-arquivos/
├── data/
│   ├── library/          # arquivos que já estão no programa
│   ├── uploads/          # arquivos novos enviados
│   └── output/           # resultados gerados
├── src/file_manager/
│   ├── bootstrap.py      # monta os casos de uso com suas dependências
│   ├── domain/
│   │   ├── entities/     # SplitResult, ConversionResult
│   │   └── exceptions/   # erros do programa
│   ├── application/
│   │   ├── interfaces/   # contratos: PdfSplitter, MarkdownConverter
│   │   └── use_cases/    # SplitPdfUseCase, ConvertToMarkdownUseCase
│   ├── infrastructure/
│   │   ├── config/       # leitura do .env
│   │   ├── pdf/          # separação de PDF (pypdf)
│   │   └── converters/   # TXT, planilhas, DOCX e PDF para Markdown
│   └── presentation/
│       ├── cli/          # comandos de terminal
│       └── streamlit_app/  # interface web (planejada)
└── tests/
    ├── unit/
    └── integration/
```

## Limitações conhecidas

- **PDFs escaneados** (só imagem) ainda não são convertidos: dependem do OCR, previsto para a Fase 5.
- **DOCX:** negrito, itálico e links viram texto simples; imagens são ignoradas; listas numeradas do Word podem virar listas com marcadores.
- **PDF:** o Markdown é gerado no modo clássico do `pymupdf4llm`. Tabelas sem bordas podem sair desalinhadas.

## Licenças

O `pymupdf4llm` (conversão de PDF) é distribuído sob licença AGPL ou licença comercial. O uso local e de estudo não exige providências, mas isso deve ser revisto antes de distribuir o programa ou oferecê-lo como serviço. Como o PDF fica atrás de um contrato, a troca da biblioteca afeta apenas uma classe.

## Privacidade

O conteúdo das pastas `data/library`, `data/uploads` e `data/output` **não é versionado** (veja o `.gitignore`), para que documentos pessoais não sejam enviados ao GitHub.

## Roadmap

- [x] Fase 1: ambiente isolado
- [x] Fase 2: estrutura base e configuração
- [x] Fase 3: separar PDF por páginas
- [x] Fase 4: converter PDF, DOCX, planilhas e TXT para Markdown
- [ ] Fase 5: OCR para PDFs escaneados
- [ ] Fase 6: mesclar arquivos em PDF
- [ ] Fase 7: interface Streamlit