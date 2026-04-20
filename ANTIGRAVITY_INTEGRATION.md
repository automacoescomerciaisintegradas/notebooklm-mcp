# 🎯 Integração com Antigravity

Guia para integrar a skill NotebookLM com Antigravity de forma completa.

---

## ⚡ Setup Automático (Recomendado)

```bash
# Navegue até a pasta da skill
cd c:\antigravity\publisher\skills\notebooklm-mcp

# Execute o script de setup
./setup_antigravity.sh

# Pronto! Reinicie Antigravity
```

---

## 🔧 Setup Manual

### 1. Instalar notebooklm-mcp-cli

```bash
# Com uv (recomendado)
uv tool install notebooklm-mcp-cli

# Ou com pip
pip install notebooklm-mcp-cli

# Verificar
nlm --version
```

### 2. Autenticar com Google

```bash
# Modo automático (navegador abre automaticamente)
nlm login

# Ou perfil nomeado
nlm login --profile antigravity
```

### 3. Configurar MCP para Antigravity

```bash
# Configuração automática
nlm setup add antigravity

# Verificar
nlm setup list
```

### 4. Localizar Arquivo de Configuração

O MCP é configurado em um destes locais:

**Windows:**
```
C:\Users\{username}\AppData\Roaming\Antigravity\settings.json
```

**macOS:**
```
~/.config/antigravity/settings.json
```

**Linux:**
```
~/.config/antigravity/settings.json
```

### 5. Verificar Configuração

Após `nlm setup add antigravity`, o arquivo deve ter:

```json
{
  "mcpServers": {
    "notebooklm-mcp": {
      "command": "notebooklm-mcp"
    }
  }
}
```

### 6. Reiniciar Antigravity

Feche e reabra a aplicação. Agora o MCP deve aparecer.

---

## ✅ Verificar Integração

### Via CLI

```bash
# Diagnóstico
nlm doctor

# Verificar autenticação
nlm login --check

# Listar notebooks (teste de conexão)
nlm notebook list
```

### Em Antigravity

Use `@notebooklm` em seus prompts:

```
@notebooklm "Crie um notebook sobre IA"

@notebooklm "Liste meus notebooks"

@notebooklm "Pesquise 'cloud trends' e crie uma apresentação"
```

---

## 📚 Usar em Workflows Antigravity

### Exemplo 1: Criar Notebook

```yaml
# ./.antigravity/workflows/research.yaml
name: create_research_notebook

steps:
  - name: Create Notebook
    skill: notebooklm-mcp
    action: notebook_create
    params:
      name: "Q2 Research"
      description: "Trimestral research project"
    output:
      notebook_id: notebook.id

  - name: Add Source
    skill: notebooklm-mcp
    action: source_add
    params:
      notebook_id: ${steps[0].notebook_id}
      url: "https://example.com/research"
```

### Exemplo 2: Pesquisa + Podcast

```yaml
name: research_and_podcast

steps:
  - name: Research
    skill: notebooklm-mcp
    action: research_start
    params:
      query: "AI trends 2026"
      depth: "comprehensive"

  - name: Create Notebook
    skill: notebooklm-mcp
    action: notebook_create
    params:
      name: "AI Trends ${now()}"

  - name: Add Sources
    skill: notebooklm-mcp
    action: batch
    foreach: ${steps[0].sources[0:10]}
    params:
      notebook_id: ${steps[1].notebook_id}
      url: ${item.url}

  - name: Generate Audio
    skill: notebooklm-mcp
    action: studio_create
    params:
      notebook_id: ${steps[1].notebook_id}
      type: "audio"
      format: "deep-dive"

  - name: Share
    skill: notebooklm-mcp
    action: notebook_share_public
    params:
      notebook_id: ${steps[1].notebook_id}
```

---

## 🚀 Uso em Prompts

### Simples

```
@notebooklm "Crie um notebook chamado 'Pesquisa' e adicione wikipedia.org"
```

### Avançado

```
@notebooklm "
1. Crie um notebook 'Product Research'
2. Pesquise 'SaaS market trends' e adicione as 5 melhores fontes
3. Gere uma apresentação
4. Compartilhe o link comigo
"
```

### Com Contexto

```
Aqui estão 3 artigos sobre IA:
- https://example1.com
- https://example2.com  
- https://example3.com

@notebooklm "Crie um notebook com esses artigos e gere um podcast de 10 minutos"
```

---

## ⚙️ Configuração Avançada

### Usar Perfil Específico

Se tem múltiplas contas Google:

```bash
# Criar perfil
nlm login --profile antigravity-work

# Usar em scripts
nlm notebook create "Project" --profile antigravity-work
```

### Aumentar Timeout

Para operações longas (pesquisa, geração de áudio):

```bash
# Windows PowerShell
$env:NOTEBOOKLM_DEVTOOLS_TIMEOUT = "60000"

# Windows CMD
set NOTEBOOKLM_DEVTOOLS_TIMEOUT=60000

# macOS/Linux
export NOTEBOOKLM_DEVTOOLS_TIMEOUT=60000
```

### Debug Logging

```bash
# Windows PowerShell
$env:NOTEBOOKLM_DEBUG = "true"

# macOS/Linux
export NOTEBOOKLM_DEBUG=true

# Então rodar comando
nlm notebook list
```

---

## 🐛 Troubleshooting

### Problema: MCP não aparece em Antigravity

**Solução 1:** Reconfigar
```bash
nlm setup add antigravity --force
```

**Solução 2:** Verificar arquivo de config
```bash
# Windows
cat $env:APPDATA\Antigravity\settings.json

# macOS/Linux
cat ~/.config/antigravity/settings.json
```

**Solução 3:** Reiniciar
```bash
# Feche Antigravity completamente
# Abra novamente
```

### Problema: Erro de autenticação

```bash
# Re-autenticar
nlm login --force

# Ou usar novo perfil
nlm login --profile antigravity-new
nlm setup add antigravity --profile antigravity-new
```

### Problema: Timeout em operações

```bash
# Aumentar timeout (em ms)
export NOTEBOOKLM_DEVTOOLS_TIMEOUT=120000

# Tentar novamente
nlm audio create "Notebook" --confirm
```

### Problema: Comandos nlm não funcionam

```bash
# Verificar instalação
uv tool list | grep notebooklm

# Se não estiver: reinstalar
uv tool install --force notebooklm-mcp-cli

# Verificar PATH
which nlm
# ou (Windows)
where nlm
```

---

## 📊 Verificação Passo a Passo

### 1. Instalação
```bash
nlm --version
# Deve mostrar: notebooklm-mcp-cli v0.5.26 (ou similar)
```

### 2. Autenticação
```bash
nlm login --check
# Deve mostrar: ✅ Authenticated
```

### 3. Conexão
```bash
nlm notebook list
# Deve mostrar: lista de notebooks
```

### 4. MCP para Antigravity
```bash
nlm setup list
# Deve incluir: antigravity
```

### 5. Diagnóstico Completo
```bash
nlm doctor
# Deve mostrar: ✅ All systems operational
```

---

## 🎯 Próximos Passos

1. ✅ Execute `./setup_antigravity.sh`
2. ✅ Reinicie Antigravity
3. ✅ Use `@notebooklm` em prompts
4. ✅ Crie seus workflows
5. ✅ Automatize suas pesquisas

---

## 💡 Dicas

- **Cache**: Antigravity fará cache das ferramentas MCP. Se houver atualizações, reinicie.
- **Context**: O MCP usa ~5-10KB de token context. Desabilite quando não usar.
- **Rate Limits**: Free tier tem ~50 queries/dia. Considere Plan Pro se precisar mais.
- **Profiles**: Use `nlm login --profile work` para múltiplas contas.

---

## 📞 Suporte

```bash
# Ajuda geral
nlm --help

# Diagnóstico completo
nlm doctor

# Ver logs
nlm --debug notebook list
```

Se tiver problemas, consulte:
- [Troubleshooting em SKILL.md](SKILL.md#-troubleshooting)
- [GitHub Issues](https://github.com/jacob-bd/notebooklm-mcp-cli/issues)

---

## ✨ Sucesso!

Você agora tem NotebookLM totalmente integrado com Antigravity! 🚀

Comande por linguagem natural:
```
@notebooklm "Crie uma pesquisa trimestral, pesquise IA trends, 
gere um podcast e compartilhe com a equipe"
```

E deixe a magia acontecer! ✨
