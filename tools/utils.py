"""
Tools — Utilitarios auxiliares para o MCP Server Manager
"""

import json
import subprocess
import sys
from pathlib import Path


def detect_running_mcp_servers():
    """Detecta servidores MCP rodando no sistema via processos."""
    try:
        import psutil
    except ImportError:
        print("psutil nao instalado. Execute: pip install psutil")
        return []

    mcp_processes = []
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cmdline = proc.info.get("cmdline") or []
            cmd_str = " ".join(cmdline).lower()
            if "mcp" in cmd_str or "nlm" in cmd_str:
                mcp_processes.append({
                    "pid": proc.info["pid"],
                    "name": proc.info["name"],
                    "cmdline": " ".join(cmdline),
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return mcp_processes


def import_servers_from_client(client_config_path: str) -> dict:
    """Importa servidores de um arquivo de configuracao de cliente MCP."""
    path = Path(client_config_path)
    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)

    return config.get("mcpServers", {})


def export_servers_to_json(servers: dict, output_path: str):
    """Exporta servidores para arquivo JSON."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"servers": servers}, f, indent=2, ensure_ascii=False)


def check_nlm_installed() -> bool:
    """Verifica se o NotebookLM MCP CLI esta instalado."""
    result = subprocess.run(
        ["nlm", "--version"],
        capture_output=True,
        text=True,
        shell=True,
    )
    return result.returncode == 0


if __name__ == "__main__":
    print("=== MCP Server Manager Tools ===\n")

    print("[1] Verificando nlm CLI...")
    if check_nlm_installed():
        print("    [OK] nlm instalado")
    else:
        print("    [!!] nlm nao encontrado")

    print("\n[2] Detectando servidores MCP rodando...")
    procs = detect_running_mcp_servers()
    if procs:
        for p in procs:
            print(f"    PID {p['pid']}: {p['cmdline'][:80]}")
    else:
        print("    Nenhum servidor MCP detectado")
