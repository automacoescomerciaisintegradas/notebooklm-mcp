# API Reference — NotebookLM MCP Skill

## Classes

### `NotebookLMClient`

Cliente Python para interagir com NotebookLM via CLI.

```python
from notebooklm_mcp import NotebookLMClient

client = NotebookLMClient(profile="default")
```

#### Métodos

##### Notebooks

```python
# Listar
notebooks = client.list_notebooks()
# → List[Dict]

# Criar
notebook = client.create_notebook("My Research", "Description")
# → Dict with 'id'

# Deletar
client.delete_notebook(notebook_id)
# → bool

# Query
response = client.query_notebook(notebook_id, "Your question")
# → str
```

##### Fontes

```python
# URL
source = client.add_source_url(notebook_id, "https://example.com")
# → Dict

# Texto
source = client.add_source_text(notebook_id, "Text content")
# → Dict

# Arquivo
source = client.add_source_file(notebook_id, "/path/to/file.pdf")
# → Dict

# Sincronizar Google Drive
sync = client.sync_drive_sources(notebook_id)
# → Dict
```

##### Studio (Geração de Conteúdo)

```python
# Áudio
audio = client.create_audio(notebook_id, format="deep-dive", confirm=True)
# → Dict with 'id'

# Vídeo
video = client.create_video(notebook_id, style="classic", confirm=True)
# → Dict with 'id'

# Slides
slides = client.create_slides(notebook_id, style="professional", confirm=True)
# → Dict with 'id'

# Revisar Slides
revised = client.revise_slides(notebook_id, "Make it more visual")
# → Dict

# Download
path = client.download_artifact(notebook_id, artifact_id, output_path="./")
# → str (file path)
```

##### Compartilhamento

```python
# Público
share = client.share_public(notebook_id)
# → Dict with 'url'

# Convidar
invite = client.share_invite(notebook_id, "user@example.com", role="viewer")
# → Dict

# Revogar
client.unshare(notebook_id, "user@example.com")
# → bool
```

##### Pesquisa

```python
# Web Research
research = client.research_start("AI trends", depth="comprehensive")
# → Dict with 'sources', 'insights'
```

##### Cross-Notebook

```python
# Query em múltiplos
results = client.cross_notebook_query(
    ["nb-1", "nb-2", "nb-3"],
    "What are the main differences?"
)
# → Dict
```

##### Batch

```python
# Criar múltiplos
notebooks = client.batch_create(["Project1", "Project2", "Project3"])
# → List[Dict]

# Query múltiplos
responses = client.batch_query(
    notebook_id,
    ["Question 1", "Question 2", "Question 3"]
)
# → List[str]
```

##### Tagging

```python
# Adicionar tag
tag = client.tag_add(notebook_id, "research")
# → Dict

# Listar tags
tags = client.tag_list()
# → List[str]

# Selecionar por tag
notebooks = client.tag_select("research")
# → List[Dict]
```

##### Pipelines

```python
# Rodar
result = client.pipeline_run("my-pipeline", params={"topic": "AI"})
# → Dict

# Listar
pipelines = client.pipeline_list()
# → List[Dict]
```

---

## Funções Globais

### Autenticação

```python
from notebooklm_mcp import (
    setup_authentication,
    setup_mcp_for_tool,
    diagnose_system
)

# Setup interativo
setup_authentication(profile="default")
# → bool

# Configurar MCP para ferramenta
setup_mcp_for_tool("antigravity")
# → bool

# Diagnosticar
status = diagnose_system()
# → Dict[str, bool]
```

### Exemplos

```python
from notebooklm_mcp import (
    example_create_and_query,
    example_research_and_podcast
)

# Exemplo 1: Criar e pergunta
notebook_id = example_create_and_query()

# Exemplo 2: Pesquisa e áudio
notebook_id, audio = example_research_and_podcast()
```

---

## CLI Commands (via `nlm`)

### Notebooks

```bash
nlm notebook list                           # Listar
nlm notebook create "Name"                  # Criar
nlm notebook delete "Name"                  # Deletar
nlm notebook query "Name" "Your question"   # Pergunta
```

### Fontes

```bash
nlm source add "Notebook" --url "https://..." # URL
nlm source add "Notebook" --text "..."        # Texto
nlm source add "Notebook" --file "path"       # Arquivo
nlm source sync "Notebook"                    # Sincronizar Drive
```

### Studio

```bash
nlm audio create "Notebook" --format deep-dive --confirm
nlm studio create "Notebook" --type video --style classic
nlm slides revise "Notebook" --revision "Make more visual"
nlm download audio "Notebook" "artifact-id" --output "./"
```

### Compartilhamento

```bash
nlm share public "Notebook"
nlm share invite "Notebook" user@example.com --role viewer
nlm share revoke "Notebook" user@example.com
```

### Pesquisa

```bash
nlm research start "AI trends" --depth comprehensive
nlm cross query "Notebook1" "Notebook2" "Your question"
```

### Batch

```bash
nlm batch create "Project1" "Project2" "Project3"
nlm batch query "Notebook" "Q1" "Q2" "Q3"
```

### Tagging

```bash
nlm tag add "Notebook" "research"
nlm tag list
nlm tag select "research"
```

### Setup & Diagnóstico

```bash
nlm setup add antigravity
nlm setup add claude-code
nlm setup list
nlm login
nlm login --check
nlm doctor
```

---

## MCP Tools (via Claude Code, Antigravity, Gemini)

Todos os métodos da `NotebookLMClient` estão disponíveis como ferramentas MCP:

- `notebook_list`
- `notebook_create`
- `notebook_delete`
- `notebook_query`
- `source_add`
- `source_sync_drive`
- `studio_create`
- `studio_revise`
- `download_artifact`
- `notebook_share_public`
- `notebook_share_invite`
- `research_start`
- `cross_notebook_query`
- `batch_create`
- `batch_query`
- `tag_add`
- `tag_list`
- `tag_select`
- `pipeline_run`
- `pipeline_list`

**Exemplo em Claude Code:**

```
@notebooklm "Create a notebook about quantum computing and generate a podcast"

@notebooklm "What are the key insights from my 'Research' notebook?"

@notebooklm "Search my notebooks with the 'important' tag and summarize"
```

---

## Error Handling

Todos os métodos podem lançar:

- `FileNotFoundError` — `nlm` não instalado
- `RuntimeError` — Comando `nlm` falhou
- `subprocess.TimeoutExpired` — Operação expirou
- `json.JSONDecodeError` — Erro ao parsear resposta

**Exemplo:**

```python
try:
    notebook = client.create_notebook("My Project")
except FileNotFoundError:
    print("Instale: uv tool install notebooklm-mcp-cli")
except RuntimeError as e:
    print(f"Erro: {e}")
```

---

## Profiles (Múltiplas Contas Google)

```python
# Perfil 1
client_work = NotebookLMClient(profile="work")

# Perfil 2
client_personal = NotebookLMClient(profile="personal")

# Adicionar profile
setup_authentication(profile="project-account")

# Listar profiles
# nlm login profile list

# Deletar profile
# nlm login profile delete work
```

---

## Logging

```python
import logging

# Habilitar debug logging
logging.basicConfig(level=logging.DEBUG)

# Usar cliente
client = NotebookLMClient()
# Agora verá logs detalhados
```

---

## Exemplo Completo

```python
from notebooklm_mcp import NotebookLMClient
import logging

logging.basicConfig(level=logging.INFO)

# Cliente
client = NotebookLMClient(profile="work")

# Pesquisar
research = client.research_start("AI safety", depth="comprehensive")

# Criar notebook
nb = client.create_notebook(
    "AI Safety Research",
    f"{len(research['sources'])} sources found"
)

# Adicionar fontes
for source in research['sources'][:10]:
    client.add_source_url(nb['id'], source['url'])

# Query
response = client.query_notebook(nb['id'], "What are the main safety concerns?")
print(response)

# Gerar áudio
audio = client.create_audio(nb['id'], format="deep-dive")
print(f"Audio: {audio['id']}")

# Compartilhar
share = client.share_public(nb['id'])
print(f"Public link: {share['url']}")
```

---

## Troubleshooting

### `nlm` não encontrado

```bash
uv tool install notebooklm-mcp-cli
```

### Erro de autenticação

```bash
nlm login --force
# ou
rm -rf ~/.notebooklm-mcp-cli
nlm login
```

### Timeout

```bash
export NOTEBOOKLM_DEVTOOLS_TIMEOUT=60000
python script.py
```

### Debug

```bash
export NOTEBOOKLM_DEBUG=true
python -c "import logging; logging.basicConfig(level=logging.DEBUG); ..."
```

---

## Recursos

- GitHub: https://github.com/jacob-bd/notebooklm-mcp-cli
- PyPI: https://pypi.org/project/notebooklm-mcp-cli/
- CLI Guide: https://github.com/jacob-bd/notebooklm-mcp-cli/blob/main/docs/CLI_GUIDE.md
- MCP Guide: https://github.com/jacob-bd/notebooklm-mcp-cli/blob/main/docs/MCP_GUIDE.md
