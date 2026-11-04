# Manipulador de Arquivos

Programa em Python para manipular arquivos, rodando localmente com interface web (Streamlit).

## Funcionalidades (planejadas)

- Separar um PDF página por página, mantendo a paginação original
- Converter PDF, DOCX, planilhas (XLSX, XLS, CSV) e TXT em Markdown
- Mesclar vários arquivos (PDF, DOCX, planilhas, TXT) em um único PDF
- Trabalhar com arquivos já existentes no programa ou com novos uploads

## Requisitos

- Windows, Python 3.12 e VS Code

## Instalação

```powershell
git clone <URL-DO-REPOSITORIO>
cd manipulador-arquivos
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
copy .env.example .env
```

## Testes

```powershell
python -m pytest
```

## Arquitetura

Clean Architecture em quatro camadas: `domain`, `application`, `infrastructure` e `presentation`.
As camadas internas nunca dependem das externas.

## Roadmap

- [x] Fase 1: ambiente isolado
- [ ] Fase 2: estrutura base e configuração
- [ ] Fase 3: separar PDF por páginas
- [ ] Fase 4: converter arquivos para Markdown
- [ ] Fase 5: mesclar arquivos em PDF
- [ ] Fase 6: interface Streamlit