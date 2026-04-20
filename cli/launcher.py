"""
NotebookLM MCP Server Manager — CLI Launcher
Gerenciamento de servidores MCP via linha de comando.
"""

import sys
import os
import json
import subprocess
from pathlib import Path

# Adicionar raiz do projeto ao path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from cli.config_util import (
    load_servers_config,
    save_servers_config,
    get_client_config_path,
    SUPPORTED_CLIENTS,
)
from cli.server_manager import ServerManager


BANNER = r"""
 _   _ _     __  __  ____ ____
| \ | | |   |  \/  |/ ___|  _ \
|  \| | |   | |\/| | |   | |_) |
| |\  | |___| |  | | |___|  __/
|_| \_|_____|_|  |_|\____|_|

  NotebookLM MCP Server Manager v1.0.0
  The AI that actually does things.
"""

MENU = """
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
"""


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    print(BANNER)


def list_servers(manager: ServerManager):
    servers = manager.list_servers()
    if not servers:
        print("\n  Nenhum servidor configurado.")
        return
    print(f"\n  {'Nome':<25} {'Status':<12} {'PID':<8} {'Porta':<8}")
    print("  " + "-" * 55)
    for s in servers:
        status = "RODANDO" if s.get("running") else "PARADO"
        pid = s.get("pid", "-")
        port = s.get("port", "-")
        print(f"  {s['name']:<25} {status:<12} {str(pid):<8} {str(port):<8}")


def start_server(manager: ServerManager):
    name = input("\n  Nome do servidor: ").strip()
    if manager.start_server(name):
        print(f"  [OK] Servidor '{name}' iniciado.")
    else:
        print(f"  [ERRO] Falha ao iniciar '{name}'.")


def stop_server(manager: ServerManager):
    name = input("\n  Nome do servidor: ").strip()
    if manager.stop_server(name):
        print(f"  [OK] Servidor '{name}' parado.")
    else:
        print(f"  [ERRO] Falha ao parar '{name}'.")


def restart_server(manager: ServerManager):
    name = input("\n  Nome do servidor: ").strip()
    manager.stop_server(name)
    if manager.start_server(name):
        print(f"  [OK] Servidor '{name}' reiniciado.")
    else:
        print(f"  [ERRO] Falha ao reiniciar '{name}'.")


def add_server(manager: ServerManager):
    print("\n  Adicionar Novo Servidor MCP")
    print("  " + "-" * 30)
    name = input("  Nome: ").strip()
    command = input("  Comando (ex: notebooklm-mcp): ").strip()
    transport = input("  Transporte [stdio/http/sse] (padrao: stdio): ").strip() or "stdio"
    port = input("  Porta (opcional): ").strip()

    server_config = {
        "name": name,
        "command": command,
        "transport": transport,
        "args": [],
        "env": {},
    }
    if port:
        server_config["port"] = int(port)

    if manager.add_server(server_config):
        print(f"  [OK] Servidor '{name}' adicionado.")
    else:
        print(f"  [ERRO] Falha ao adicionar '{name}'.")


def remove_server(manager: ServerManager):
    name = input("\n  Nome do servidor para remover: ").strip()
    confirm = input(f"  Tem certeza que deseja remover '{name}'? [s/N]: ").strip().lower()
    if confirm == "s":
        if manager.remove_server(name):
            print(f"  [OK] Servidor '{name}' removido.")
        else:
            print(f"  [ERRO] Servidor '{name}' nao encontrado.")


def view_logs(manager: ServerManager):
    name = input("\n  Nome do servidor: ").strip()
    logs = manager.get_logs(name)
    if logs:
        print(f"\n  --- Logs de '{name}' ---")
        print(logs[-2000:])  # Ultimas 2000 chars
    else:
        print(f"  Nenhum log encontrado para '{name}'.")


def show_status(manager: ServerManager):
    print("\n  Status Geral")
    print("  " + "=" * 55)
    servers = manager.list_servers()
    running = sum(1 for s in servers if s.get("running"))
    stopped = len(servers) - running
    print(f"  Total: {len(servers)} | Rodando: {running} | Parados: {stopped}")
    print()
    list_servers(manager)


def configure_client(manager: ServerManager):
    print("\n  Configurar Cliente MCP")
    print("  " + "-" * 30)
    for i, client in enumerate(SUPPORTED_CLIENTS, 1):
        print(f"  [{i}] {client}")
    choice = input("\n  Escolha: ").strip()
    try:
        idx = int(choice) - 1
        client = SUPPORTED_CLIENTS[idx]
        config_path = get_client_config_path(client)
        print(f"\n  Cliente: {client}")
        print(f"  Config:  {config_path}")
        if manager.configure_client(client):
            print(f"  [OK] Cliente '{client}' configurado com sucesso!")
        else:
            print(f"  [ERRO] Falha ao configurar '{client}'.")
    except (ValueError, IndexError):
        print("  [ERRO] Opcao invalida.")


def main():
    manager = ServerManager(PROJECT_ROOT)

    while True:
        clear_screen()
        print_banner()
        print(MENU)
        choice = input("  > ").strip()

        if choice == "1":
            list_servers(manager)
        elif choice == "2":
            start_server(manager)
        elif choice == "3":
            stop_server(manager)
        elif choice == "4":
            restart_server(manager)
        elif choice == "5":
            add_server(manager)
        elif choice == "6":
            remove_server(manager)
        elif choice == "7":
            view_logs(manager)
        elif choice == "8":
            show_status(manager)
        elif choice == "9":
            configure_client(manager)
        elif choice == "0":
            print("\n  Ate logo!")
            sys.exit(0)
        else:
            print("  Opcao invalida.")

        input("\n  Pressione Enter para continuar...")


if __name__ == "__main__":
    main()
