@echo off
title NotebookLM MCP Server Manager - CLI
echo.
echo  Iniciando NotebookLM MCP Server Manager (CLI)...
echo.
cd /d "%~dp0"
python -m cli.launcher
pause
