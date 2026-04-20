@echo off
title NotebookLM MCP Server Manager - GUI
echo.
echo  Iniciando NotebookLM MCP Server Manager (GUI)...
echo.
cd /d "%~dp0"
python -m gui.app
