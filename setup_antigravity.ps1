#
# setup_antigravity.ps1 — Setup automático do NotebookLM MCP para Antigravity
#
# Uso: .\setup_antigravity.ps1 -Profile "default"
#
# Exemplos:
#   .\setup_antigravity.ps1
#   .\setup_antigravity.ps1 -Profile "work"
#   .\setup_antigravity.ps1 -Profile "personal"
#

param(
    [string]$Profile = "default"
)

# Cores
$Yellow = "`e[1;33m"
$Green = "`e[0;32m"
$Red = "`e[0;31m"
$NC = "`e[0m" # No Color

# Adicionar bin local ao PATH
$localBinPath = "$env:USERPROFILE\.local\bin"
if (-not ($env:PATH -like "*$localBinPath*")) {
    $env:PATH = "$localBinPath;$env:PATH"
}

Write-Host "$Yellow`🚀 Setup NotebookLM MCP para Antigravity$NC" -NoNewline
Write-Host ""
Write-Host ""

# 1. Verificar se uv está instalado
Write-Host "📦 Verificando ferramentas..."
$uvExists = $null -ne (Get-Command uv -ErrorAction SilentlyContinue)
if (-not $uvExists) {
    Write-Host "$Red❌ uv não encontrado. Instale em: https://docs.astral.sh/uv/getting-started/installation/$NC"
    exit 1
}
Write-Host "$Green✅ uv encontrado$NC"
Write-Host ""

# 2. Instalar ou atualizar pacote
Write-Host "$Yellow📥 Instalando notebooklm-mcp-cli...$NC"
uv tool install notebooklm-mcp-cli --upgrade

if ($LASTEXITCODE -ne 0) {
    Write-Host "$Red❌ Erro ao instalar notebooklm-mcp-cli$NC"
    exit 1
}

# 3. Verificar versão
Write-Host ""
Write-Host "🔍 Versão instalada:"
uv tool list | Select-String "notebooklm"

# 4. Autenticar
Write-Host ""
Write-Host "$Yellow🔐 Autenticação NotebookLM (perfil: $Profile)$NC"
Write-Host "Seu navegador será aberto. Faça login com sua conta Google."
Write-Host ""
nlm login --profile $Profile

if ($LASTEXITCODE -ne 0) {
    Write-Host "$Red❌ Erro na autenticação$NC"
    exit 1
}

# 5. Verificar autenticação
Write-Host ""
Write-Host "$Yellow✅ Verificando autenticação...$NC"
nlm login --check --profile $Profile

# 6. Configurar MCP para Antigravity
Write-Host ""
Write-Host "$Yellow⚙️  Configurando MCP para Antigravity...$NC"
nlm setup add antigravity

if ($LASTEXITCODE -ne 0) {
    Write-Host "$Red⚠️  Aviso: Setup automático pode não ter funcionado$NC"
    Write-Host "Execute manualmente: nlm setup add antigravity"
}

# 7. Diagnosticar
Write-Host ""
Write-Host "$Yellow🏥 Diagnóstico...$NC"
nlm doctor

# 8. Sucesso!
Write-Host ""
Write-Host "$Green════════════════════════════════════════$NC"
Write-Host "$Green✅ Setup concluído!$NC"
Write-Host "$Green════════════════════════════════════════$NC"
Write-Host ""
Write-Host "Próximos passos:"
Write-Host "1. Reinicie Antigravity"
Write-Host "2. Use @notebooklm nos seus prompts"
Write-Host "3. Veja exemplos em: ./examples/"
Write-Host ""
Write-Host "Comandos úteis:"
Write-Host "  nlm notebook list              # Listar notebooks"
Write-Host "  nlm notebook create 'Projeto'  # Criar notebook"
Write-Host "  nlm setup list                 # Ver configurações"
Write-Host "  nlm login profile list         # Ver perfis"
Write-Host ""
