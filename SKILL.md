---
name: notebooklm-mcp
description: >
  Acesso programático ao Google NotebookLM via CLI e MCP Server. Integra com Antigravity,
  Claude Code, Gemini e scripts Python/Bash para criar notebooks, adicionar fontes, gerar
  conteúdo (áudio, vídeo, apresentações), pesquisar e automatizar workflows com NotebookLM.
---

# NotebookLM MCP & CLI — Integração Programática

Acesso completo ao Google NotebookLM através de:
- **CLI (`nlm`)** — Comandos de terminal para automação
- **MCP Server** — Integração com assistentes de IA
- **Python API** — Funções para scripts e workflows
- **Antigravity Skills** — Integração nativa

---

## 🚀 Instalação Rápida

### 1. Instalar o Pacote (via `uv` recomendado)

```bash
# Opção A: Instalação recomendada (uv)
uv tool install notebooklm-mcp-cli

# Opção B: Instalação via pip
pip install notebooklm-mcp-cli

# Opção C: Rodar sem instalar (uvx)
uvx --from notebooklm-mcp-cli nlm --help
```

### 2. Autenticação

```bash
# Auto mode (recomendado) — abre o navegador, você faz login, cookies extraídos automaticamente
nlm login

# Verificar autenticação
nlm login --check

# Múltiplas contas Google (perfis nomeados)
nlm login --profile work
nlm login --profile personal
```

### 3. Configurar MCP para Antigravity / Claude Code / Gemini

```bash
# Configuração automática
nlm setup add antigravity          # Antigravity
nlm setup add claude-code          # Claude Code / Desktop
nlm setup add gemini               # Gemini CLI
nlm setup add cursor               # Cursor

# Verificar configurações
nlm setup list

# Diagnosticar problemas
nlm doctor
```

---

## 📚 Recursos Disponíveis

### CLI — 35+ Comandos

```bash
# Notebooks
nlm notebook list                           # Listar todos
nlm notebook create "Research Project"      # Criar
nlm notebook delete <notebook>              # Deletar
nlm notebook query <notebook> "sua pergunta"# Perguntar

# Fontes
nlm source add <notebook> --url "https://..." # Adicionar URL
nlm source add <notebook> --text "conteúdo"  # Adicionar texto
nlm source add <notebook> --file "caminho"   # Adicionar arquivo
nlm source sync <notebook>                   # Sincronizar Google Drive

# Geração de Conteúdo (Studio)
nlm audio create <notebook> --confirm        # Gerar áudio/podcast
nlm studio create <notebook> --type video    # Gerar vídeo
nlm slides revise <notebook>                 # Revisar deck
nlm download audio <notebook> <artifact-id> # Baixar arquivo

# Compartilhamento
nlm share public <notebook>                  # Publicar
nlm share invite <notebook> user@email.com  # Convidar

# Operações em Batch
nlm batch query <notebook> "pergunta1" "pergunta2"
nlm batch create "Projeto1" "Projeto2"

# Workflows (Pipelines)
nlm pipeline run <pipeline-name>
nlm pipeline list

# Pesquisa
nlm research start "deep research query"    # Pesquisa com IA
nlm cross query <notebook1> <notebook2>     # Query em múltiplos

# Tagging & Seleção Inteligente
nlm tag add <notebook> "research"
nlm tag select "research"               # Selecionar por tag
```

### MCP Server — 35 Ferramentas (Tools)

Disponíveis em Claude Code, Antigravity, Gemini CLI:

| Ferramenta | Função |
|---|---|
| `notebook_list` | Listar notebooks |
| `notebook_create` | Criar novo notebook |
| `notebook_query` | Perguntar ao notebook |
| `source_add` | Adicionar fonte (URL, texto, arquivo) |
| `source_sync_drive` | Sincronizar com Google Drive |
| `studio_create` | Gerar áudio, vídeo, apresentação |
| `studio_revise` | Revisar conteúdo gerado |
| `download_artifact` | Baixar arquivo gerado |
| `notebook_share_*` | Compartilhar notebook |
| `batch_*` | Operações em lote |
| `research_start` | Pesquisa com IA |
| `cross_notebook_query` | Query cross-notebook |
| `pipeline_run` | Rodar workflows |
| `tag_*` | Gerenciar tags |

---

## 🎯 Exemplos de Uso

### CLI — Workflow Simples

```bash
# 1. Criar notebook
nlm notebook create "AI Trends 2026"

# 2. Adicionar fonte via URL
nlm source add "AI Trends 2026" --url "https://arxiv.org/list/cs.AI/recent"

# 3. Perguntar ao notebook
nlm notebook query "AI Trends 2026" "Quais são as tendências em IA para 2026?"

# 4. Gerar áudio
nlm audio create "AI Trends 2026" --confirm

# 5. Compartilhar
nlm share public "AI Trends 2026"
```

### Python — API Programática

```python
from notebooklm_mcp.cli import NotebookLMClient

# Inicializar cliente
client = NotebookLMClient()

# Criar notebook
notebook = client.create_notebook("Research Project")
notebook_id = notebook['id']

# Adicionar fonte
client.add_source(notebook_id, url="https://example.com/article")

# Fazer query
response = client.query(notebook_id, "Summarize key findings")
print(response)

# Gerar áudio
audio_job = client.create_audio(notebook_id)
print(f"Gerando áudio... {audio_job['id']}")
```

### MCP — Em Claude Code / Antigravity

Simplesmente use linguagem natural:

```
"Crie um notebook chamado 'Pesquisa de Mercado' e adicione esses artigos: 
https://example1.com e https://example2.com"

"Gere um áudio podcast deep-dive sobre este notebook"

"Liste todos meus notebooks e diga quantas fontes cada um tem"

"Pergunte ao notebook 'Product Strategy': Quais são os principais riscos?"
```

### MCP — Em Gemini CLI

```
@notebooklm "Crie uma apresentação sobre IA Generativa com as melhores práticas"

@notebooklm "Pesquise 'enterprise AI adoption' e crie um notebook com os resultados"
```

### Antigravity — Integração Nativa

```yaml
# lobster.yaml
workflows:
  research_and_podcast:
    steps:
      - skill: notebooklm-mcp
        action: notebook_create
        params:
          name: "Quarterly Research"
      
      - skill: notebooklm-mcp
        action: source_add
        params:
          notebook: ${steps[0].id}
          url: "https://example.com/research"
      
      - skill: notebooklm-mcp
        action: studio_create
        params:
          notebook: ${steps[0].id}
          type: "audio"
          format: "deep-dive"
      
      - skill: notebooklm-mcp
        action: download_artifact
        params:
          artifact_id: ${steps[2].id}
          output_path: "./podcasts/"
```

---

## 🔐 Autenticação & Segurança

### Lifecycle de Autenticação

| Componente | Validade | Renovação |
|---|---|---|
| Cookies | ~2-4 semanas | Auto-refresh (headless browser) |
| CSRF Token | ~minutos | Auto-refresh em falha |
| Session ID | Por sessão | Extraído automaticamente |

### Múltiplos Perfis (Multi-Account)

```bash
# Perfil 1 (work)
nlm login --profile work

# Perfil 2 (personal)  
nlm login --profile personal

# Listar perfis
nlm login profile list

# Alternar padrão
nlm login switch personal

# Deletar perfil
nlm login profile delete work
```

### Navegadores Suportados

- Chrome
- Arc
- Brave
- Edge
- Chromium
- Firefox (experimental)

```bash
# Especificar navegador preferido
nlm config set auth.browser arc
nlm login
```

---

## ⚙️ Configuração Avançada

### Variáveis de Ambiente

```bash
# Timeout para DevTools (em ms)
export NOTEBOOKLM_DEVTOOLS_TIMEOUT=30000

# Debug logging
export NOTEBOOKLM_DEBUG=true

# Caminho customizado para cookies
export NOTEBOOKLM_CONFIG_DIR="~/.config/notebooklm-custom"

# Provider de CDP (Chrome DevTools Protocol) externo
export NOTEBOOKLM_CDP_URL="http://127.0.0.1:18800"
```

### MCP Server — Opções de Transporte

#### Stdio (Default)
```json
{
  "mcpServers": {
    "notebooklm-mcp": {
      "command": "notebooklm-mcp"
    }
  }
}
```

#### HTTP (para uso remoto)
```json
{
  "mcpServers": {
    "notebooklm-mcp": {
      "command": "notebooklm-mcp",
      "args": ["--transport", "http", "--port", "3000"]
    }
  }
}
```

#### SSE (Server-Sent Events)
```json
{
  "mcpServers": {
    "notebooklm-mcp": {
      "command": "notebooklm-mcp",
      "args": ["--transport", "sse", "--port", "3001"]
    }
  }
}
```

### Limitar Context Window

⚠️ O MCP fornece 35 ferramentas. Desabilite quando não usar NotebookLM:

**Claude Code:**
```
Desabilitar: /mcp disable @notebooklm-mcp
Habilitar: /mcp enable @notebooklm-mcp
```

**Cursor:**
```
Remover temporariamente do settings.json
```

---

## 📊 Casos de Uso Reais

### 1. Pesquisa Automática + Podcast Semanal

```bash
#!/bin/bash
# research_and_podcast.sh

TOPIC="AI Trends"
DATE=$(date +%Y%m%d)
NOTEBOOK="$TOPIC - $DATE"

# Criar notebook
nlm notebook create "$NOTEBOOK"

# Pesquisar e adicionar fontes
nlm research start "latest $TOPIC" | jq '.sources[].url' | while read url; do
  nlm source add "$NOTEBOOK" --url "$url"
done

# Gerar áudio
nlm audio create "$NOTEBOOK" --confirm

# Baixar
ARTIFACT_ID=$(nlm notebook query "$NOTEBOOK" --json | jq '.artifacts[-1].id')
nlm download audio "$NOTEBOOK" "$ARTIFACT_ID" --output "podcasts/$DATE.mp3"

# Publicar
nlm share public "$NOTEBOOK"
echo "✅ Podcast criado e publicado: $NOTEBOOK"
```

### 2. Análise Cross-Notebook com AI

```python
import subprocess
import json

def cross_notebook_analysis(notebook_ids, question):
    """Perguntar a múltiplos notebooks e comparar respostas"""
    results = {}
    
    for nb_id in notebook_ids:
        response = subprocess.run(
            ["nlm", "notebook", "query", nb_id, question, "--json"],
            capture_output=True,
            text=True
        )
        results[nb_id] = json.loads(response.stdout)
    
    return results

# Usar com Claude/Gemini via MCP
answers = cross_notebook_analysis(
    ["notebook-1", "notebook-2", "notebook-3"],
    "Qual é o principal desafio mencionado?"
)
```

### 3. Pipeline: Pesquisa → Notebook → Slides → Compartilhamento

```yaml
# research_pipeline.yaml
name: quarterly_research

steps:
  - name: research
    type: research
    config:
      query: "enterprise AI adoption 2026"
      depth: "comprehensive"
      results_limit: 20
  
  - name: create_notebook
    type: notebook_create
    params:
      name: "Q2 Research - Enterprise AI"
      description: "Compiled from latest research"
  
  - name: add_sources
    type: batch
    foreach: ${steps.research.sources}
    action: source_add
    params:
      notebook: ${steps.create_notebook.id}
      url: ${item.url}
  
  - name: generate_slides
    type: studio_create
    params:
      notebook: ${steps.create_notebook.id}
      type: "slides"
      style: "professional"
  
  - name: share
    type: notebook_share_invite
    params:
      notebook: ${steps.create_notebook.id}
      emails: 
        - "team@company.com"
        - "cto@company.com"
      role: "viewer"
```

---

## 🐛 Troubleshooting

### Problema: "Authentication failed" ou cookies expirados

```bash
# Solução 1: Re-autenticar
nlm login

# Solução 2: Usar perfil nomeado
nlm login --profile work --force

# Solução 3: Remover cache e reiniciar
rm -rf ~/.notebooklm-mcp-cli
nlm login
```

### Problema: MCP não aparece em Claude Code / Antigravity

```bash
# Reconfigar
nlm setup add claude-code --force
nlm setup add antigravity --force

# Reiniciar a aplicação

# Se ainda não funcionar
nlm doctor
```

### Problema: `uv tool upgrade` não instala versão mais recente

```bash
# Solução: Forçar reinstalação
uv tool install --force notebooklm-mcp-cli
```

### Problema: Timeout em operações longas (pesquisa, geração de áudio)

```bash
# Aumentar timeout via env var (em ms)
export NOTEBOOKLM_DEVTOOLS_TIMEOUT=60000
nlm audio create <notebook> --confirm
```

---

## 📖 Documentação Completa

- **[CLI Guide](https://github.com/jacob-bd/notebooklm-mcp-cli/blob/main/docs/CLI_GUIDE.md)** — Referência de todos os comandos
- **[MCP Guide](https://github.com/jacob-bd/notebooklm-mcp-cli/blob/main/docs/MCP_GUIDE.md)** — Todas as 35 ferramentas com exemplos
- **[Authentication](https://github.com/jacob-bd/notebooklm-mcp-cli/blob/main/docs/AUTHENTICATION.md)** — Setup e troubleshooting detalhado
- **[API Reference](https://github.com/jacob-bd/notebooklm-mcp-cli/blob/main/docs/API_REFERENCE.md)** — Documentação interna (para contribuidores)

---

## ⚠️ Importante

- Usa **APIs internas não-documentadas** do Google NotebookLM (podem mudar)
- Cookies precisam ser extraídos do navegador
- Rate limits no free tier (~50 queries/dia)
- Sem suporte oficial do Google
- **Use para fins pessoais/experimentais**

---

## 🔗 Links Úteis

- **GitHub**: https://github.com/jacob-bd/notebooklm-mcp-cli
- **PyPI**: https://pypi.org/project/notebooklm-mcp-cli/
- **Issues**: https://github.com/jacob-bd/notebooklm-mcp-cli/issues
- **Changelog**: https://github.com/jacob-bd/notebooklm-mcp-cli/blob/main/CHANGELOG.md

---

## 📝 Exemplos da Skill

Veja a pasta `examples/` para scripts prontos:
- `setup_antigravity.sh` — Setup automático
- `research_automation.sh` — Pesquisa e podcast semanal
- `cross_notebook_analysis.py` — Análise de múltiplos notebooks
- `batch_operations.py` — Operações em lote
- `pipeline_example.yaml` — Workflow multi-step
