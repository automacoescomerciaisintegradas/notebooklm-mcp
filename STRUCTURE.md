# NotebookLM MCP Skill — Estrutura Completa

Este é um resumo da skill criada para integrar Google NotebookLM com Antigravity, Claude Code, Gemini e outros assistentes de IA.

---

## 📁 Arquivos Criados

```
notebooklm-mcp/
├── SKILL.md                          # Documentação completa
├── README.md                         # Guia rápido
├── GETTING_STARTED.md               # 5 minutos de setup
├── API_REFERENCE.md                 # Referência de funções
├── skill.py                         # Implementação Python (NotebookLMClient)
├── __init__.py                      # Pacote Python
│
├── examples/
│   ├── simple_example.py            # Exemplo básico
│   ├── cross_notebook_analysis.py   # Análise multi-notebook
│   ├── batch_operations.py          # Operações em lote
│   ├── research_automation.sh       # Automação pesquisa + podcast
│   ├── setup_antigravity.sh         # Setup automático
│   └── workflow_example.yaml        # Workflow completo
│
└── LICENSE                          # MIT License (referência)
```

---

## 🎯 O que Você Pode Fazer

### CLI — Terminal
```bash
nlm notebook create "Research"
nlm source add "Research" --url "..."
nlm notebook query "Research" "Question?"
nlm audio create "Research" --confirm
nlm share public "Research"
```

### Python — Scripts & Automação
```python
from notebooklm_mcp import NotebookLMClient

client = NotebookLMClient()
nb = client.create_notebook("Project")
client.add_source_url(nb['id'], "https://...")
response = client.query_notebook(nb['id'], "?")
```

### MCP — Claude Code, Antigravity, Gemini
```
"Crie um notebook sobre IA e gere um podcast"
"Pesquise 'tendências 2026' e crie uma apresentação"
"Analise meus notebooks e resuma descobertas"
```

### Antigravity Workflows
```yaml
- skill: notebooklm-mcp
  action: notebook_create
  params:
    name: "Quarterly Research"

- skill: notebooklm-mcp
  action: source_add
  params:
    notebook: ${steps[0].id}
    url: "https://example.com"
```

---

## 🚀 35+ Ferramentas Disponíveis

| Categoria | Ferramentas |
|---|---|
| **Notebooks** | `notebook_list`, `notebook_create`, `notebook_delete`, `notebook_query` |
| **Fontes** | `source_add`, `source_sync_drive` |
| **Studio** | `studio_create`, `studio_revise`, `download_artifact` |
| **Compartilhamento** | `notebook_share_public`, `notebook_share_invite` |
| **Pesquisa** | `research_start`, `cross_notebook_query` |
| **Batch** | `batch_create`, `batch_query`, `batch_*` |
| **Tagging** | `tag_add`, `tag_list`, `tag_select` |
| **Pipelines** | `pipeline_run`, `pipeline_list` |

---

## 💻 Como Usar

### Opção 1: Setup Rápido
```bash
./setup_antigravity.sh
```

### Opção 2: Manual
```bash
# 1. Instalar
uv tool install notebooklm-mcp-cli

# 2. Fazer login
nlm login

# 3. Configurar
nlm setup add antigravity

# 4. Reiniciar Antigravity
```

### Opção 3: Python
```bash
python examples_simple_example.py
```

---

## 📖 Documentação

| Arquivo | Conteúdo |
|---|---|
| **SKILL.md** | Documentação completa (35+ comandos, exemplos, troubleshooting) |
| **GETTING_STARTED.md** | Setup em 5 minutos |
| **API_REFERENCE.md** | Referência de funções Python e MCP |
| **README.md** | Guia rápido |
| **examples/** | Scripts prontos para usar |

---

## 🔧 Integração Rápida

### Com Antigravity
```bash
nlm setup add antigravity
```

### Com Claude Code
```bash
nlm setup add claude-code
```

### Com Gemini
```bash
nlm setup add gemini
```

### Com Cursor
```bash
nlm setup add cursor
```

---

## 📊 Exemplos Inclusos

1. **simple_example.py** — Criar notebook, adicionar fonte, perguntar
2. **research_automation.sh** — Pesquisa web → notebook → áudio → compartilhamento
3. **cross_notebook_analysis.py** — Fazer pergunta a múltiplos notebooks
4. **batch_operations.py** — Criar/query em lote com paralelização
5. **workflow_example.yaml** — Pipeline trimestral completo

---

## 🎓 Casos de Uso

### 1. Pesquisa Automática Semanal
```bash
./examples_research_automation.sh "AI Trends"
```

### 2. Análise Cross-Notebook
```bash
python examples_cross_notebook_analysis.py nb-1 nb-2 nb-3 \
  --question "Principais insights?"
```

### 3. Geração Batch de Conteúdo
```bash
python examples_batch_operations.py --action audio \
  --notebooks nb-1 nb-2 nb-3
```

### 4. Pipeline Trimestral
```yaml
nlm pipeline run quarterly_research
```

---

## ✅ Checklist de Setup

- [ ] `uv tool install notebooklm-mcp-cli`
- [ ] `nlm login`
- [ ] `nlm setup add antigravity` (ou sua ferramenta)
- [ ] Reiniciar aplicação
- [ ] `nlm doctor` (verificar)
- [ ] `nlm notebook list` (testar)
- [ ] Ler [GETTING_STARTED.md](GETTING_STARTED.md)

---

## 🐛 Troubleshooting

```bash
# Diagnóstico completo
nlm doctor

# Re-autenticar
nlm login --force

# Ver logs detalhados
export NOTEBOOKLM_DEBUG=true
nlm notebook list
```

Mais: [SKILL.md#-troubleshooting](SKILL.md#-troubleshooting)

---

## 🔗 Referências

- **GitHub**: https://github.com/jacob-bd/notebooklm-mcp-cli
- **PyPI**: https://pypi.org/project/notebooklm-mcp-cli/
- **CLI Guide**: https://github.com/jacob-bd/notebooklm-mcp-cli/blob/main/docs/CLI_GUIDE.md
- **MCP Guide**: https://github.com/jacob-bd/notebooklm-mcp-cli/blob/main/docs/MCP_GUIDE.md

---

## ⚙️ Autenticação Multi-Perfil

```bash
# Múltiplas contas Google
nlm login --profile work
nlm login --profile personal

# Usar em código
client = NotebookLMClient(profile="work")

# Listar perfis
nlm login profile list

# Mudar padrão
nlm login switch personal

# Deletar
nlm login profile delete work
```

---

## 💡 Próximos Passos

1. ✅ **Setup**: Execute `./setup_antigravity.sh`
2. 📚 **Learn**: Leia [GETTING_STARTED.md](GETTING_STARTED.md)
3. 🔬 **Experiment**: Execute os exemplos em `examples/`
4. 🚀 **Integrate**: Use em seus workflows
5. 📖 **Reference**: Consulte [API_REFERENCE.md](API_REFERENCE.md)

---

## 📝 Nota Importante

⚠️ Esta skill utiliza **APIs internas não-documentadas** do Google NotebookLM. Podem mudar sem aviso. Use para fins pessoais/experimentais.

- Rate limits: ~50 queries/dia (free tier)
- Cookies expiram a cada ~2-4 semanas
- Sem suporte oficial do Google

---

## 🎉 Sucesso!

Você tem acesso programático completo ao Google NotebookLM via:
- ✅ CLI (`nlm`)
- ✅ Python (`NotebookLMClient`)
- ✅ MCP Server (Claude, Gemini, Antigravity)
- ✅ Workflows & Automação
- ✅ Integração com ferramentas favoritas

**Divirta-se construindo!** 🚀
