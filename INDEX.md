# 📑 Índice Completo — NotebookLM MCP Skill

Bem-vindo! Esta skill integra Google NotebookLM com Antigravity, Claude Code, Gemini e oferece CLI + Python API.

---

## 🚀 Comece Aqui

| Objetivo | Arquivo | Tempo |
|---|---|---|
| **Começar em 5 minutos** | [GETTING_STARTED.md](GETTING_STARTED.md) | 5 min ⚡ |
| **Integrar com Antigravity** | [ANTIGRAVITY_INTEGRATION.md](ANTIGRAVITY_INTEGRATION.md) | 10 min |
| **Ver guia rápido** | [README.md](README.md) | 2 min |
| **Documentação completa** | [SKILL.md](SKILL.md) | 30 min 📚 |

---

## 📚 Documentação por Tipo

### Setup & Instalação
- **[GETTING_STARTED.md](GETTING_STARTED.md)** — 5 passos para começar
- **[ANTIGRAVITY_INTEGRATION.md](ANTIGRAVITY_INTEGRATION.md)** — Integração completa com Antigravity
- **[README.md](README.md)** — Guia rápido (1 página)

### Uso & Referência
- **[SKILL.md](SKILL.md)** — Documentação completa (35+ comandos, MCP tools, exemplos)
- **[API_REFERENCE.md](API_REFERENCE.md)** — Referência de funções Python e MCP
- **[STRUCTURE.md](STRUCTURE.md)** — Visão geral da estrutura

### Código & Exemplos
- **[examples_simple_example.py](examples_simple_example.py)** — Hello World em Python
- **[examples_research_automation.sh](examples_research_automation.sh)** — Pesquisa + Podcast automático
- **[examples_cross_notebook_analysis.py](examples_cross_notebook_analysis.py)** — Análise cross-notebook
- **[examples_batch_operations.py](examples_batch_operations.py)** — Operações em lote
- **[examples_workflow.yaml](examples_workflow.yaml)** — Workflow completo em YAML

### Configuração
- **[setup_antigravity.sh](setup_antigravity.sh)** — Script de setup automático

---

## 🎯 Por Caso de Uso

### Quero... 

**...começar rapidinho** → [GETTING_STARTED.md](GETTING_STARTED.md)

**...usar com Antigravity** → [ANTIGRAVITY_INTEGRATION.md](ANTIGRAVITY_INTEGRATION.md)

**...usar com Claude Code** → [SKILL.md - MCP Configuration](SKILL.md#mcp-configuration)

**...usar com Gemini** → [SKILL.md - MCP Configuration](SKILL.md#mcp-configuration)

**...entender os comandos CLI** → [SKILL.md - CLI Features](SKILL.md#features) ou `nlm --help`

**...programar em Python** → [API_REFERENCE.md](API_REFERENCE.md)

**...executar exemplos prontos** → [examples/](.)

**...criar workflows** → [examples_workflow.yaml](examples_workflow.yaml)

**...resolver um problema** → [SKILL.md - Troubleshooting](SKILL.md#-troubleshooting)

**...ver o que é possível fazer** → [SKILL.md - What You Can Do](SKILL.md#what-you-can-do)

---

## 📖 Fluxo Recomendado

### Iniciante (30 minutos)

1. Leia [README.md](README.md) (2 min)
2. Siga [GETTING_STARTED.md](GETTING_STARTED.md) (5 min)
3. Execute [examples_simple_example.py](examples_simple_example.py) (10 min)
4. Use em [ANTIGRAVITY_INTEGRATION.md](ANTIGRAVITY_INTEGRATION.md) (10 min)

### Intermediário (1 hora)

1. Leia [SKILL.md](SKILL.md) - Primeiras 50 linhas
2. Execute um dos exemplos em `examples/`
3. Crie seu próprio script Python seguindo [API_REFERENCE.md](API_REFERENCE.md)
4. Integre com seu workflow

### Avançado (2+ horas)

1. Leia [SKILL.md](SKILL.md) - Tudo
2. Leia [API_REFERENCE.md](API_REFERENCE.md)
3. Estude os exemplos avançados
4. Crie seus próprios workflows/pipelines

---

## 🔗 Mapa de Conteúdo

```
ÍNDICE (você está aqui)
│
├─ 🚀 INÍCIO RÁPIDO
│  ├─ GETTING_STARTED.md
│  ├─ ANTIGRAVITY_INTEGRATION.md
│  └─ README.md
│
├─ 📚 DOCUMENTAÇÃO COMPLETA
│  ├─ SKILL.md (main)
│  ├─ API_REFERENCE.md
│  └─ STRUCTURE.md
│
├─ 💻 CÓDIGO & EXEMPLOS
│  ├─ examples_simple_example.py
│  ├─ examples_research_automation.sh
│  ├─ examples_cross_notebook_analysis.py
│  ├─ examples_batch_operations.py
│  └─ examples_workflow.yaml
│
├─ 🔧 IMPLEMENTAÇÃO
│  ├─ skill.py (NotebookLMClient)
│  ├─ __init__.py
│  └─ setup_antigravity.sh
│
└─ 📋 META
   └─ INDEX.md (este arquivo)
```

---

## 🌟 Destaques Principais

### CLI (Terminal)
```bash
nlm notebook create "Research"
nlm source add "Research" --url "https://..."
nlm notebook query "Research" "Question?"
nlm audio create "Research" --confirm
```
👉 Veja: [SKILL.md - CLI Features](SKILL.md#features)

### Python (Scripts)
```python
from notebooklm_mcp import NotebookLMClient
client = NotebookLMClient()
```
👉 Veja: [API_REFERENCE.md](API_REFERENCE.md)

### MCP (IA Assistants)
```
@notebooklm "Crie um notebook e gere um podcast"
```
👉 Veja: [ANTIGRAVITY_INTEGRATION.md](ANTIGRAVITY_INTEGRATION.md)

### Workflows (Automação)
```yaml
- skill: notebooklm-mcp
  action: notebook_create
```
👉 Veja: [examples_workflow.yaml](examples_workflow.yaml)

---

## ⚡ Comandos Rápidos

```bash
# Setup em 1 linha
./setup_antigravity.sh

# Listar notebooks
nlm notebook list

# Criar e testar
nlm notebook create "Test"
nlm notebook query "Test" "Hello?"

# Python exemplo
python examples_simple_example.py

# Diagnóstico
nlm doctor
```

---

## 🎓 Recursos Inclusos

| Tipo | Quantidade | Exemplos |
|---|---|---|
| **CLI Commands** | 35+ | `nlm notebook create`, `nlm audio create`, etc |
| **MCP Tools** | 35+ | `notebook_create`, `studio_create`, etc |
| **Python Methods** | 25+ | `create_notebook()`, `query_notebook()`, etc |
| **Examples** | 5 | simple, research, cross-analysis, batch, workflow |
| **Docs** | 7 | Getting started, API ref, Antigravity, etc |

---

## 📊 Capacidades

### ✅ O que você pode fazer

- ✅ Criar/listar/deletar notebooks
- ✅ Adicionar fontes (URL, texto, arquivo, Google Drive)
- ✅ Perguntar ao notebook (persistent history)
- ✅ Gerar áudio podcasts (vários formatos)
- ✅ Gerar vídeos
- ✅ Criar apresentações
- ✅ Gerar flashcards, infográficos, mind maps
- ✅ Pesquisar na web com IA
- ✅ Query cross-notebook
- ✅ Operações em lote
- ✅ Compartilhar (público, com convite)
- ✅ Sincronizar Google Drive
- ✅ Tagging inteligente
- ✅ Pipelines/workflows

### ⚠️ Limitações

- ⚠️ APIs internas (podem mudar)
- ⚠️ Rate limits free tier (~50 queries/dia)
- ⚠️ Cookies expiram ~2-4 semanas
- ⚠️ Sem suporte oficial do Google
- ⚠️ Use para fins pessoais/experimentais

---

## 🔧 Suporte Técnico

### Se tiver problema...

1. Consulte **[SKILL.md - Troubleshooting](SKILL.md#-troubleshooting)**
2. Execute `nlm doctor`
3. Veja **[ANTIGRAVITY_INTEGRATION.md - Troubleshooting](ANTIGRAVITY_INTEGRATION.md#-troubleshooting)**
4. Verifique **[GitHub Issues](https://github.com/jacob-bd/notebooklm-mcp-cli/issues)**

### Comandos de Diagnóstico

```bash
nlm doctor                  # Diagnóstico completo
nlm login --check          # Verificar autenticação
nlm setup list             # Listar configurações
nlm --help                 # Ajuda geral
export NOTEBOOKLM_DEBUG=true  # Debug mode
```

---

## 🌐 Referências Externas

- **GitHub oficial**: https://github.com/jacob-bd/notebooklm-mcp-cli
- **PyPI package**: https://pypi.org/project/notebooklm-mcp-cli/
- **CLI Guide**: https://github.com/jacob-bd/notebooklm-mcp-cli/blob/main/docs/CLI_GUIDE.md
- **MCP Guide**: https://github.com/jacob-bd/notebooklm-mcp-cli/blob/main/docs/MCP_GUIDE.md

---

## 🎯 Próximos Passos

1. ✅ **Instalar**: `uv tool install notebooklm-mcp-cli`
2. ✅ **Autenticar**: `nlm login`
3. ✅ **Configurar**: `nlm setup add antigravity`
4. ✅ **Testar**: `nlm notebook list`
5. ✅ **Explorar**: Veja os exemplos

---

## 💡 Dicas Úteis

- 🔹 Leia [GETTING_STARTED.md](GETTING_STARTED.md) primeiro
- 🔹 Use `nlm doctor` para diagnosticar qualquer problema
- 🔹 Consulte [API_REFERENCE.md](API_REFERENCE.md) para código Python
- 🔹 Estude os exemplos em `examples/` para boas práticas
- 🔹 Use `@notebooklm` em prompts do Antigravity
- 🔹 Configure múltiplos perfis para múltiplas contas Google

---

## 🎉 Bem-vindo!

Você agora tem acesso programático total ao Google NotebookLM! 

**Comece**: [GETTING_STARTED.md](GETTING_STARTED.md)

**Integre com Antigravity**: [ANTIGRAVITY_INTEGRATION.md](ANTIGRAVITY_INTEGRATION.md)

**Aprenda tudo**: [SKILL.md](SKILL.md)

---

**Last updated**: 19 de abril de 2026  
**Version**: notebooklm-mcp-cli v0.5.26+  
**Skill**: NotebookLM MCP for Antigravity
