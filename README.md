<div align="center">

# 🧠 NotebookLM MCP Skill

### *The AI that actually does things.*

**Acesso programático ao Google NotebookLM** via CLI, Python, MCP Server e Antigravity.

Gerencia seus projetos, cria sistemas e executa tarefas reais.<br>
Tudo local, privado e 100% sob seu controle.

[![NotebookLM](https://img.shields.io/badge/Google-NotebookLM-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://notebooklm.google.com/notebook/89c832c9-11ec-49d3-a406-0ccac77a2f5e?authuser=1)
[![MCP](https://img.shields.io/badge/MCP-Server-blueviolet?style=for-the-badge)](https://modelcontextprotocol.io/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

[Documentação Completa](SKILL.md) · [Início Rápido](GETTING_STARTED.md) · [API Reference](API_REFERENCE.md) · [Exemplos](examples_simple_example.py)

</div>

---

## 🤖 Bem-vindo(a) ao Futuro da Criação de Conteúdo!

Uma **skill completa** que integra o Google NotebookLM com qualquer assistente de IA — crie notebooks, adicione fontes, gere podcasts, faça pesquisas e automatize workflows, tudo via comandos ou linguagem natural.

### O que você ganha:

- **35+ comandos CLI** — automação total via terminal
- **35 ferramentas MCP** — integração com Antigravity, Claude Code, Gemini, Cursor
- **Python API** — 25+ métodos para scripts e workflows
- **Multi-perfil** — múltiplas contas Google simultâneas
- **Geração de conteúdo** — áudio/podcast, vídeo, slides, pesquisa com IA

---

## ⚡ Setup em 3 Passos

### 1. Instalar

```bash
# Via uv (recomendado)
uv tool install notebooklm-mcp-cli

# Ou via pip
pip install notebooklm-mcp-cli
```

### 2. Autenticar

```bash
nlm login
```

### 3. Configurar MCP

```bash
nlm setup add antigravity     # Antigravity / Cleudocode
nlm setup add claude-code     # Claude Code / Desktop
nlm setup add gemini          # Gemini CLI
nlm setup add cursor          # Cursor
```

> ✅ **Pronto!** Use `nlm doctor` para verificar tudo.

---

## 📖 Como Usar

### CLI — Terminal

```bash
# Criar notebook + adicionar fonte + perguntar + gerar podcast
nlm notebook create "Pesquisa IA 2026"
nlm source add "Pesquisa IA 2026" --url "https://arxiv.org/list/cs.AI/recent"
nlm notebook query "Pesquisa IA 2026" "Quais tendências em IA para 2026?"
nlm audio create "Pesquisa IA 2026" --confirm
```

### Python — Scripts & Automação

```python
from notebooklm_mcp import NotebookLMClient

client = NotebookLMClient()
nb = client.create_notebook("Meu Projeto")
client.add_source_url(nb['id'], "https://example.com")
response = client.query_notebook(nb['id'], "Resuma os principais pontos")
print(response)
```

### MCP — Linguagem Natural (Antigravity / Claude / Gemini)

```
"Crie um notebook sobre IA Generativa e gere um podcast deep-dive"

"Pesquise 'cloud trends 2026' e crie uma apresentação"

"Liste meus notebooks e resuma cada um"
```

---

## 📂 Estrutura do Projeto

```
notebooklm-mcp/
├── README.md                         # Este arquivo
├── SKILL.md                          # Documentação completa (35+ comandos, 35 tools)
├── GETTING_STARTED.md               # Guia de 5 minutos
├── API_REFERENCE.md                 # Referência de API Python
├── ANTIGRAVITY_INTEGRATION.md       # Integração com Antigravity
├── SETUP_WINDOWS.md                 # Setup específico Windows
├── STRUCTURE.md                     # Mapa de arquivos
│
├── skill.py                         # Implementação Python (NotebookLMClient)
├── __init__.py                      # Pacote Python
│
├── setup_antigravity.ps1            # Setup automático (Windows)
├── setup_antigravity.sh             # Setup automático (Linux/Mac)
├── setup_antigravity.bat            # Setup automático (CMD)
│
├── examples_simple_example.py       # Exemplo básico
├── examples_cross_notebook_analysis.py  # Análise multi-notebook
├── examples_batch_operations.py     # Operações em lote
├── examples_research_automation.sh  # Pesquisa + podcast automático
└── examples_workflow.yaml           # Workflow YAML completo
```

---

## 🎯 Casos de Uso

| Caso de Uso | Ferramenta | Descrição |
|---|---|---|
| Pesquisa + Podcast Semanal | CLI + Bash | Automatize pesquisa e gere áudio |
| Análise multi-notebook | Python API | Compare insights de múltiplos notebooks |
| Assistente integrado | MCP Server | Use linguagem natural em qualquer IDE |
| Workflow automatizado | Antigravity | Pipelines completos de conteúdo |
| Compartilhamento em equipe | CLI | Publique e convide colaboradores |

---

## 📊 Referência Rápida de Comandos

```bash
# Notebooks
nlm notebook list                            # Listar todos
nlm notebook create "Nome"                   # Criar
nlm notebook delete <id>                     # Deletar
nlm notebook query <id> "pergunta"           # Perguntar

# Fontes
nlm source add <id> --url "https://..."      # URL
nlm source add <id> --file "arquivo.pdf"     # Arquivo
nlm source add <id> --text "conteúdo"        # Texto

# Geração de Conteúdo
nlm audio create <id> --confirm              # Podcast/áudio
nlm studio create <id> --type video          # Vídeo
nlm studio create <id> --type slides         # Slides

# Compartilhamento
nlm share public <id>                        # Publicar
nlm share invite <id> user@email.com         # Convidar

# Operações em Lote
nlm batch query <id> "q1" "q2" "q3"         # Múltiplas perguntas
nlm batch create "Proj1" "Proj2"             # Múltiplos notebooks

# Pesquisa com IA
nlm research start "deep research query"     # Pesquisa avançada
nlm cross query <id1> <id2>                  # Cross-notebook

# Diagnóstico
nlm doctor                                   # Verificar tudo
nlm login --check                            # Status da autenticação
nlm setup list                               # Configurações MCP
```

---

## ⚠️ Notas Importantes

- Usa APIs internas não-documentadas do Google NotebookLM
- Rate limits no free tier (~50 queries/dia)
- Cookies expiram a cada ~2-4 semanas (re-autentique com `nlm login`)
- Use para fins pessoais e experimentais

---

## 📚 Documentação

| Documento | Descrição |
|---|---|
| [SKILL.md](SKILL.md) | Documentação completa — todos os comandos, ferramentas MCP, exemplos |
| [GETTING_STARTED.md](GETTING_STARTED.md) | Setup em 5 minutos |
| [API_REFERENCE.md](API_REFERENCE.md) | Referência Python API |
| [ANTIGRAVITY_INTEGRATION.md](ANTIGRAVITY_INTEGRATION.md) | Integração nativa Antigravity |
| [SETUP_WINDOWS.md](SETUP_WINDOWS.md) | Guia específico Windows |

---

## 🔗 Links

- [📓 Notebook de Referência](https://notebooklm.google.com/notebook/89c832c9-11ec-49d3-a406-0ccac77a2f5e?authuser=1)
- [📦 PyPI — notebooklm-mcp-cli](https://pypi.org/project/notebooklm-mcp-cli/)
- [🛠️ CLI Guide](https://github.com/jacob-bd/notebooklm-mcp-cli/blob/main/docs/CLI_GUIDE.md)
- [🔌 MCP Guide](https://github.com/jacob-bd/notebooklm-mcp-cli/blob/main/docs/MCP_GUIDE.md)
- [🏢 ACI — Automações Comerciais Integradas](https://github.com/automacoescomerciaisintegradas)

---

<div align="center">

## 💬 Contato & Suporte

[![WhatsApp](https://img.shields.io/badge/WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)](https://wa.me/558894227586)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:contato@automacoescomerciais.com.br)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/automacoescomerciaisintegradas)

---

**© Automações Comerciais Integradas 2026 ⚙️ Todos os direitos reservados.**

*The AI that actually does things.*

</div>
