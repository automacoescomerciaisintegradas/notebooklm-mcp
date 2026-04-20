# 🚀 Guia de Início Rápido — NotebookLM MCP Skill

## ⚡ 5 Minutos de Setup

### 1️⃣ Instalar Pacote

```bash
uv tool install notebooklm-mcp-cli
# ou: pip install notebooklm-mcp-cli
```

### 2️⃣ Fazer Login

```bash
nlm login
# Seu navegador abre automaticamente, faça login no Google
```

### 3️⃣ Configurar MCP

**Para Antigravity:**
```bash
nlm setup add antigravity
```

**Para Claude Code:**
```bash
nlm setup add claude-code
```

**Para Gemini CLI:**
```bash
nlm setup add gemini
```

### 4️⃣ Reiniciar Ferramenta

- Antigravity: Reinicie a aplicação
- Claude Code: `/mcp` para reconectar
- Gemini: Reinicie a sessão CLI

### 5️⃣ Usar!

**Terminal:**
```bash
nlm notebook create "My Project"
nlm source add "My Project" --url "https://example.com"
nlm notebook query "My Project" "Your question?"
```

**Python:**
```python
from notebooklm_mcp import NotebookLMClient
client = NotebookLMClient()
nb = client.create_notebook("Project")
```

**Claude/Gemini/Antigravity:**
```
"Crie um notebook sobre IA e gere um áudio"
```

---

## 📚 Próximos Passos

| Próximo | Comando/Link |
|---|---|
| Ver todos os notebooks | `nlm notebook list` |
| Diagnosticar problemas | `nlm doctor` |
| Documentação completa | [SKILL.md](SKILL.md) |
| Referência da API | [API_REFERENCE.md](API_REFERENCE.md) |
| Exemplos | `./examples/` |
| Múltiplas contas | `nlm login --profile work` |

---

## 💡 Exemplos Rápidos

### CLI — Criar Pesquisa

```bash
# Criar notebook
nlm notebook create "AI Research"

# Adicionar fonte
nlm source add "AI Research" --url "https://arxiv.org/list/cs.AI/recent"

# Perguntar
nlm notebook query "AI Research" "Quais são as tendências?"

# Gerar áudio
nlm audio create "AI Research" --confirm
```

### Python — Automação

```python
from notebooklm_mcp import NotebookLMClient

client = NotebookLMClient()

# Criar
nb = client.create_notebook("Research")

# Adicionar fontes
client.add_source_url(nb['id'], "https://example.com/article1")
client.add_source_url(nb['id'], "https://example.com/article2")

# Perguntar
response = client.query_notebook(nb['id'], "Resumo?")
print(response)

# Gerar áudio
audio = client.create_audio(nb['id'], format="deep-dive")

# Compartilhar
share = client.share_public(nb['id'])
print(f"Link: {share['url']}")
```

### Antigravity — Natural Language

```
"Crie um notebook 'Tendências 2026' com estes artigos:
https://example1.com
https://example2.com
E gere um podcast"
```

---

## 🎯 Casos de Uso Comuns

### Pesquisa Semanal + Podcast

```bash
./examples_research_automation.sh "AI Trends"
```

### Análise de Múltiplos Notebooks

```bash
python examples_cross_notebook_analysis.py nb-1 nb-2 nb-3 \
  --question "Quais são os principais desafios?"
```

### Operações em Lote

```bash
python examples_batch_operations.py --action create \
  --names "Project1" "Project2" "Project3"
```

### Workflow Completo

```bash
nlm pipeline run quarterly_research
```

---

## ⚠️ Problemas Comuns

| Problema | Solução |
|---|---|
| `nlm: command not found` | `uv tool install notebooklm-mcp-cli` |
| `Authentication failed` | `nlm login --force` |
| MCP não aparece em Claude Code | Reinicie a aplicação |
| Timeout em operações longas | `export NOTEBOOKLM_DEVTOOLS_TIMEOUT=60000` |

Mais: `nlm doctor`

---

## 🔗 Documentação

- 📖 [Guia Completo (SKILL.md)](SKILL.md)
- 🔧 [Referência da API (API_REFERENCE.md)](API_REFERENCE.md)
- 💾 [Exemplos](./examples/)
- 🐛 [Troubleshooting](SKILL.md#-troubleshooting)

---

## 📞 Suporte

```bash
# Ajuda geral
nlm --help

# Diagnóstico completo
nlm doctor

# IA assistant
nlm --ai
```

---

## 🎉 Sucesso!

Você agora tem acesso programático total ao Google NotebookLM!

**Próximas ideias:**
- ✅ Pesquisa automática semanal
- ✅ Integração com seus workflows
- ✅ Análise cross-notebook com IA
- ✅ Pipeline de geração de conteúdo
- ✅ Compartilhamento com stakeholders
