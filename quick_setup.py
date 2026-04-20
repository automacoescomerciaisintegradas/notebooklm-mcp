#!/usr/bin/env python3
"""
Quick Setup — NotebookLM MCP Server Manager
Instala dependencias e configura o ambiente automaticamente.
"""

import subprocess
import sys
import os
from pathlib import Path


def run(cmd, desc):
    print(f"  [*] {desc}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  [OK] {desc}")
    else:
        print(f"  [!!] {desc} - {result.stderr.strip()[:200]}")
    return result.returncode == 0


def main():
    print()
    print("=" * 55)
    print("  NotebookLM MCP Server Manager - Quick Setup")
    print("  (c) Automacoes Comerciais Integradas 2026")
    print("=" * 55)
    print()

    project_root = Path(__file__).parent

    # 1. Verificar Python
    py_version = sys.version_info
    print(f"  Python: {py_version.major}.{py_version.minor}.{py_version.micro}")
    if py_version < (3, 10):
        print("  [!!] Python 3.10+ e necessario.")
        sys.exit(1)

    # 2. Instalar dependencias
    requirements = project_root / "requirements.txt"
    if requirements.exists():
        run(f"{sys.executable} -m pip install -r {requirements}", "Instalar dependencias")
    else:
        print("  [~] requirements.txt nao encontrado, pulando...")

    # 3. Instalar notebooklm-mcp-cli via uv (se disponivel)
    uv_check = subprocess.run("uv --version", shell=True, capture_output=True, text=True)
    if uv_check.returncode == 0:
        run("uv tool install notebooklm-mcp-cli", "Instalar NotebookLM MCP CLI (via uv)")
    else:
        print("  [~] uv nao encontrado. Instale com: pip install uv")

    # 4. Criar diretorios necessarios
    for d in ["logs", "config"]:
        (project_root / d).mkdir(exist_ok=True)
    print("  [OK] Diretorios criados")

    # 5. Garantir configs iniciais
    servers_json = project_root / "config" / "servers.json"
    if not servers_json.exists():
        import json
        default = {"servers": {"notebooklm-mcp": {
            "name": "notebooklm-mcp",
            "command": "nlm",
            "args": ["serve"],
            "transport": "stdio",
            "env": {},
        }}}
        with open(servers_json, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2)
        print("  [OK] servers.json criado com servidor padrao")
    else:
        print("  [OK] servers.json ja existe")

    print()
    print("  Setup completo!")
    print()
    print("  Para iniciar:")
    print("    CLI:  python -m cli.launcher")
    print("    GUI:  python -m gui.app")
    print("    Ou:   cli-launcher.bat / gui-launcher.bat")
    print()


if __name__ == "__main__":
    main()
