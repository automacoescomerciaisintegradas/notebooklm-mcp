<div align="center">

# 🧠 NotebookLM MCP Server Manager

### *The AI that actually does things.*

**Gerenciador completo de servidores MCP** para Cursor, Claude Desktop e Antigravity.<br>
Interface CLI e GUI para gerenciar, monitorar e configurar servidores MCP com facilidade.

[![NotebookLM](https://img.shields.io/badge/Google-NotebookLM-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://notebooklm.google.com/notebook/89c832c9-11ec-49d3-a406-0ccac77a2f5e?authuser=1)
[![MCP](https://img.shields.io/badge/MCP-Protocol-blueviolet?style=for-the-badge)](https://modelcontextprotocol.io/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-informational?style=for-the-badge)]()
[![Security](https://img.shields.io/badge/Security-Guard%20v1.1.0-red?style=for-the-badge&logo=shield&logoColor=white)]()

[Documentação](SKILL.md) · [Início Rápido](#-quick-start) · [CLI](#-interface-cli) · [GUI](#-interface-gui) · [SecurityGuard](#-securityguard--protocolo-de-defesa-preditiva) · [API](API_REFERENCE.md)

</div>

---

## 🎯 O que é?

Um **gerenciador de servidores MCP (Model Context Protocol)** que oferece interfaces **CLI** e **GUI** para controlar servidores MCP usados por assistentes de IA como Cursor, Claude Desktop e Antigravity.

### Principais Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| 🖥️ **Triple Interface** | CLI interativa + GUI desktop (Tkinter) + Web dashboard (Flask) |
| 🔄 **Gerenciamento Completo** | Iniciar, parar, reiniciar e monitorar servidores |
| 📊 **Logs em Tempo Real** | Visualize logs de cada servidor instantaneamente |
| 🔌 **Auto-configuração** | Exporta para Cursor, Claude Desktop e Antigravity |
| 🌐 **Multi-servidor** | Gerencie múltiplos servidores MCP simultaneamente |
| 💾 **Persistência** | Configurações salvas em JSON |
| �️ **SecurityGuard** | Protocolo de Defesa Preditiva contra comandos destrutivos |
| �🔍 **Detecção de Processos** | Encontra servidores MCP já rodando no sistema |
| 🛡️ **35+ Ferramentas MCP** | Integração completa com NotebookLM |

---

## ⚡ Quick Start

### Opção 1 — Setup Automático

```bash
python quick_setup.py
```

### Opção 2 — Manual

```bash
# 1. Clonar
git clone https://github.com/automacoescomerciaisintegradas/notebooklm-mcp.git
cd notebooklm-mcp

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Instalar NotebookLM MCP CLI
uv tool install notebooklm-mcp-cli

# 4. Autenticar
nlm login
```

### Iniciar

```bash
# CLI interativa
python -m cli.launcher
# ou: cli-launcher.bat

# GUI desktop (Tkinter)
python -m gui.app
# ou: gui-launcher.bat

# Web dashboard (navegador)
python -m web.app
# ou: web-launcher.bat
# Acesse: http://localhost:5117
```

---

## 🖥️ Interface CLI

Menu interativo com todas as operações de gerenciamento:

```
 _   _ _     __  __  ____ ____
| \ | | |   |  \/  |/ ___|  _ \
|  \| | |   | |\/| | |   | |_) |
| |\  | |___| |  | | |___|  __/
|_| \_|_____|_|  |_|\____|_|

  NotebookLM MCP Server Manager v1.0.0

  [1] Listar servidores MCP
  [2] Iniciar servidor
  [3] Parar servidor
  [4] Reiniciar servidor
  [5] Adicionar novo servidor
  [6] Remover servidor
  [7] Ver logs de um servidor
  [8] Status de todos os servidores
  [9] Configurar cliente (Cursor/Claude/Antigravity)
  [0] Sair
```

---

## 🎨 Interface GUI

Interface gráfica moderna com tema escuro inspirado no design system ACI:

- **Painel esquerdo** — Lista de servidores com status em tempo real
- **Painel direito** — Detalhes, ações e logs do servidor selecionado
- **Botões de ação** — Iniciar, Parar, Reiniciar, Remover, Configurar Cliente
- **Auto-refresh** — Atualização automática a cada 3 segundos

> Para capturas de tela, veja a pasta `gui/assets/screenshots/`

---

## 🌐 Interface Web

Dashboard completo acessivel pelo navegador em `http://localhost:5117`:

- **Dashboard** — Cards de servidores com status, PID e acoes em tempo real
- **SecurityGuard** — Metricas, violacoes recentes e validacao de comandos
- **Clientes** — Configurar Cursor, Claude Desktop e Antigravity com 1 clique
- **Logs** — Visualizador de logs por servidor
- **Validar Comando** — Teste qualquer comando contra o SecurityGuard
- **Auto-refresh** — Atualizacao automatica a cada 4 segundos
- **API REST** — 16 endpoints para integracao programatica

### API REST Endpoints

| Metodo | Endpoint | Descricao |
|---|---|---|
| GET | `/api/servers` | Listar servidores |
| POST | `/api/servers` | Adicionar servidor |
| DELETE | `/api/servers/<name>` | Remover servidor |
| POST | `/api/servers/<name>/start` | Iniciar servidor |
| POST | `/api/servers/<name>/stop` | Parar servidor |
| POST | `/api/servers/<name>/restart` | Reiniciar servidor |
| GET | `/api/servers/<name>/info` | Detalhes do servidor |
| GET | `/api/servers/<name>/logs` | Logs do servidor |
| POST | `/api/servers/<name>/logs/clear` | Limpar logs |
| GET | `/api/clients` | Listar clientes |
| POST | `/api/clients/<client>/configure` | Configurar cliente |
| GET | `/api/security/status` | Status do SecurityGuard |
| POST | `/api/security/validate` | Validar comando |
| GET | `/api/config` | Ler configuracao |
| PUT | `/api/config` | Atualizar configuracao |
| GET | `/api/health` | Health check |

---

## 🔌 Compatibilidade

| Cliente | Suporte | Auto-config | Caminho da Config |
|---|---|---|---|
| **Cursor** | ✅ | ✅ | `~/.cursor/mcp.json` |
| **Claude Desktop** (Win) | ✅ | ✅ | `%APPDATA%/Claude/claude_desktop_config.json` |
| **Claude Desktop** (macOS) | ✅ | ✅ | `~/Library/Application Support/Claude/...` |
| **Antigravity** | ✅ | ✅ | `~/.antigravity/mcp.json` |

---

## 📂 Estrutura do Projeto

```
notebooklm-mcp/
│
├── core/                             # Módulos centrais
│   ├── __init__.py
│   └── security_guard.py            # SecurityGuard — Defesa Preditiva
│
├── cli/                              # Interface de Linha de Comando
│   ├── __init__.py
│   ├── launcher.py                   # Menu principal CLI
│   ├── server_manager.py            # Gerenciamento de processos
│   └── config_util.py               # Utilitários de configuração
│
├── gui/                              # Interface Gráfica
│   ├── __init__.py
│   ├── app.py                        # Aplicação principal Tkinter
│   └── assets/                       # Ícones, screenshots, vídeos
│       ├── screenshots/
│       └── videos/
│
├── mcp_server/                       # Wrapper do servidor MCP
│   ├── __init__.py
│   └── server.py                     # Comunicação JSON-RPC stdio
│
├── config/                           # Configurações persistentes
│   ├── servers.json                  # Servidores cadastrados
│   ├── app_config.json              # Preferências do app
│   └── security.json                # Padrões SecurityGuard
│
├── tests/                            # Testes automatizados
│   ├── test_manager.py
│   └── test_security.py             # 14 cenários de segurança
│
├── tools/                            # Utilitários auxiliares
│   └── utils.py                      # Detecção de processos, import/export
│
├── logs/                             # Logs dos servidores
├── docs/                             # Documentação adicional
│
├── SKILL.md                          # Documentação completa (35+ comandos)
├── GETTING_STARTED.md               # Guia de 5 minutos
├── API_REFERENCE.md                 # Referência Python API
├── ANTIGRAVITY_INTEGRATION.md       # Integração Antigravity
├── SETUP_WINDOWS.md                 # Setup Windows
│
├── skill.py                         # NotebookLM Client Python
├── __init__.py                      # Pacote Python
│
├── cli-launcher.bat                 # Launcher CLI (Windows)
├── gui-launcher.bat                 # Launcher GUI (Windows)
├── quick_setup.py                   # Setup automático
├── requirements.txt                 # Dependências Python
│
├── setup_antigravity.ps1            # Setup Antigravity (PowerShell)
├── setup_antigravity.sh             # Setup Antigravity (Bash)
├── setup_antigravity.bat            # Setup Antigravity (CMD)
│
├── examples_simple_example.py
├── examples_cross_notebook_analysis.py
├── examples_batch_operations.py
├── examples_research_automation.sh
└── examples_workflow.yaml
```

---

## 📖 Como Usar o NotebookLM MCP

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

# Diagnóstico
nlm doctor                                   # Verificar tudo
nlm login --check                            # Status da autenticação
```

---

## 🛡️ SecurityGuard — Protocolo de Defesa Preditiva

> **v1.1.0** — Camada de defesa proativa que impede a execução de comandos potencialmente destrutivos.

O SecurityGuard valida **cada comando** contra uma lista negra de expressões regulares (Regex) antes da execução, bloqueando operações perigosas automaticamente.

### O que é Bloqueado por Padrão

| Categoria | Exemplos | Severidade |
|---|---|---|
| **Destruição de filesystem** | `rm -rf /`, `format C:`, `dd if=... of=/dev/` | CRITICAL |
| **SQL destrutivo** | `DROP TABLE`, `DELETE FROM ... ;`, `TRUNCATE TABLE` | CRITICAL |
| **Execução remota (RCE)** | `curl ... \| sh`, `Invoke-Expression DownloadString` | CRITICAL |
| **Git destrutivo** | `git push --force`, `git reset --hard` | HIGH |
| **Env vars perigosas** | `LD_PRELOAD`, `DYLD_INSERT_LIBRARIES` | HIGH |
| **Path traversal** | `../../../etc/passwd`, `.ssh/id_rsa` | HIGH |
| **Processos críticos** | `kill -9 1`, `taskkill /f /im csrss` | CRITICAL |
| **Crypto/Ransomware** | `openssl enc -aes ... -in /`, `gpg --encrypt *.*` | CRITICAL |

### Como Personalizar Padrões

Edite `config/security.json`:

```json
{
  "dangerousCommandBlocking": {
    "enabled": true,
    "customPatterns": [
      {
        "pattern": "^my-dangerous-script",
        "description": "Bloqueia scripts específicos por nome",
        "severity": "HIGH"
      },
      {
        "pattern": "DROP TABLE",
        "description": "Proteção contra SQL Injection acidental",
        "severity": "CRITICAL"
      },
      {
        "pattern": "DELETE FROM",
        "description": "Blindagem de banco de dados",
        "severity": "CRITICAL"
      }
    ],
    "allowedPatterns": []
  }
}
```

### Monitoramento via CLI

```
  > S

  SecurityGuard - Protocolo de Defesa Preditiva
  ==================================================
  Status:    ATIVO
  Padroes:   37 bloqueados
  Violacoes: 0 detectadas nesta sessao

  Nenhuma violacao detectada. Sistema seguro.

  Config: config/security.json
  Logs:   logs/security.log
```

### Uso Programático

```python
from core.security_guard import SecurityGuard

guard = SecurityGuard()

# Validar comando
result = guard.validate_command("rm -rf /")
if not result.is_safe:
    print(f"BLOQUEADO: {result.violation.description}")
    # BLOQUEADO: rm -rf (remocao forcada recursiva)

# Validar variáveis de ambiente
result = guard.validate_env_vars({"LD_PRELOAD": "/tmp/evil.so"})

# Validar caminhos de arquivo
result = guard.validate_file_path("../../../etc/passwd")

# Adicionar padrão em runtime
guard.add_pattern(r"^meu-script-perigoso", "Bloqueio customizado", "HIGH")

# Resumo de violações
summary = guard.get_violations_summary()
```

---

## 🧪 Testes

```bash
# Testes do gerenciador
python -m tests.test_manager

# Testes de segurança (14 cenários)
python -m tests.test_security

# Todos os testes
python -m tests.test_manager && python -m tests.test_security
```

---

## 🛡️ Segurança

- **SecurityGuard** — Protocolo de Defesa Preditiva com 35+ padrões regex
- **Bloqueio dinâmico** — Valida cada comando antes da execução
- **Configuração soberana** — Controle total via `config/security.json`
- **Log de auditoria** — Todas as violações em `logs/security.log`
- Credenciais armazenadas localmente (cookies do navegador)
- Nenhum dado enviado para servidores de terceiros
- Comunicação MCP via stdio (sem rede externa)

---

## ❓ FAQ

**P: Preciso de conta Google?**
R: Sim, o NotebookLM requer autenticação Google via `nlm login`.

**P: Funciona em Linux/macOS?**
R: Sim! CLI e GUI funcionam em qualquer sistema com Python 3.10+.

**P: Como atualizar os cookies expirados?**
R: Execute `nlm login --clear` para re-autenticar.

**P: Posso adicionar servidores MCP de outros projetos?**
R: Sim! Use "Adicionar servidor" na CLI ou GUI para registrar qualquer servidor MCP.

---

## 📚 Documentação

| Documento | Descrição |
|---|---|
| [SKILL.md](SKILL.md) | Documentação completa — 35+ comandos, 35 ferramentas MCP |
| [GETTING_STARTED.md](GETTING_STARTED.md) | Setup em 5 minutos |
| [API_REFERENCE.md](API_REFERENCE.md) | Referência Python API |
| [ANTIGRAVITY_INTEGRATION.md](ANTIGRAVITY_INTEGRATION.md) | Integração Antigravity |
| [SETUP_WINDOWS.md](SETUP_WINDOWS.md) | Guia Windows |

---

## 🔗 Links

- [📓 Notebook de Referência](https://notebooklm.google.com/notebook/89c832c9-11ec-49d3-a406-0ccac77a2f5e?authuser=1)
- [📦 PyPI — notebooklm-mcp-cli](https://pypi.org/project/notebooklm-mcp-cli/)
- [🔌 MCP Protocol](https://modelcontextprotocol.io/)
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
