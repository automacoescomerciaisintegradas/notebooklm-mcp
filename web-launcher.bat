@echo off
title NotebookLM MCP Server Manager - Web
echo.
echo  Iniciando Web Interface...
echo  Acesse: http://localhost:5117
echo.
cd /d "%~dp0"
python -m web.app
