@echo off
REM setup_antigravity.bat — Setup automático do NotebookLM MCP para Antigravity
REM
REM Uso: setup_antigravity.bat [profile]
REM
REM Exemplos:
REM   setup_antigravity.bat
REM   setup_antigravity.bat work
REM   setup_antigravity.bat personal
REM

setlocal enabledelayedexpansion

set PROFILE=%1
if "%PROFILE%"=="" set PROFILE=default

echo.
echo 🚀 Setup NotebookLM MCP para Antigravity
echo.

REM 1. Verificar se uv está instalado
echo 📦 Verificando ferramentas...
where uv >nul 2>nul
if errorlevel 1 (
    echo ❌ uv não encontrado. Instale em: https://docs.astral.sh/uv/getting-started/installation/
    exit /b 1
)
echo ✅ uv encontrado
echo.

REM 2. Instalar ou atualizar pacote
echo 📥 Instalando notebooklm-mcp-cli...
call uv tool install notebooklm-mcp-cli --upgrade
if errorlevel 1 (
    echo ❌ Erro ao instalar notebooklm-mcp-cli
    exit /b 1
)

REM 3. Verificar versão
echo.
echo 🔍 Versão instalada:
call uv tool list | findstr "notebooklm"

REM 4. Autenticar
echo.
echo 🔐 Autenticação NotebookLM (perfil: %PROFILE%)
echo Seu navegador será aberto. Faça login com sua conta Google.
echo.
call nlm login --profile %PROFILE%
if errorlevel 1 (
    echo ❌ Erro na autenticação
    exit /b 1
)

REM 5. Verificar autenticação
echo.
echo ✅ Verificando autenticação...
call nlm login --check --profile %PROFILE%

REM 6. Configurar MCP para Antigravity
echo.
echo ⚙️  Configurando MCP para Antigravity...
call nlm setup add antigravity
if errorlevel 1 (
    echo ⚠️  Aviso: Setup automático pode não ter funcionado
    echo Execute manualmente: nlm setup add antigravity
)

REM 7. Diagnosticar
echo.
echo 🏥 Diagnóstico...
call nlm doctor

REM 8. Sucesso!
echo.
echo ════════════════════════════════════════
echo ✅ Setup concluído!
echo ════════════════════════════════════════
echo.
echo Próximos passos:
echo 1. Reinicie Antigravity
echo 2. Use @notebooklm nos seus prompts
echo 3. Veja exemplos em: .\examples\
echo.
echo Comandos úteis:
echo   nlm notebook list              # Listar notebooks
echo   nlm notebook create "Projeto"  # Criar notebook
echo   nlm setup list                 # Ver configurações
echo   nlm login profile list         # Ver perfis
echo.
