# TARS Vision Skill - Windows Launcher (PowerShell)
# Inicializa os componentes de visão do TARS no Windows

# Busca o venv na pasta atual ou em pastas superiores (até 4 níveis)
$VENV_PATH = ""
$current_dir = Get-Item "."
for ($i = 0; $i -lt 5; $i++) {
    $potential_path = Join-Path $current_dir.FullName "venv\Scripts\Activate.ps1"
    if (Test-Path $potential_path) {
        $VENV_PATH = $potential_path
        break
    }
    $current_dir = $current_dir.Parent
    if ($null -eq $current_dir) { break }
}

# Ativa o ambiente virtual se ele existir
if ($VENV_PATH -ne "") {
    & $VENV_PATH
    Write-Host "✅ Ambiente virtual encontrado e ativado: $VENV_PATH" -ForegroundColor Cyan
} else {
    Write-Host "⚠️ Ambiente virtual não encontrado. Usando Python global." -ForegroundColor Yellow
}

# Tenta encontrar o melhor comando para o Python
$PYTHON_CMD = "python"
if (Get-Command "py" -ErrorAction SilentlyContinue) {
    $PYTHON_CMD = "py"
} elseif (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Erro: Python não encontrado! Instale o Python ou ajuste o PATH." -ForegroundColor Red
    exit 1
}

Write-Host "🐍 Usando: $(Get-Command $PYTHON_CMD | Select-Object -ExpandProperty Source)" -ForegroundColor Gray

# Inicia o Face Server (Flask) em segundo plano
Write-Host "🚀 Iniciando Face Server..." -ForegroundColor Green
Start-Process $PYTHON_CMD -ArgumentList "-u assets/face_server.py" -NoNewWindow

# Inicia o Vision Router (Gestures) em segundo plano
Write-Host "🚀 Iniciando Vision Router..." -ForegroundColor Green
Start-Process $PYTHON_CMD -ArgumentList "-u assets/vision_router.py" -NoNewWindow

Write-Host "🤖 TARS Vision skill inicializado com sucesso." -ForegroundColor Magenta
