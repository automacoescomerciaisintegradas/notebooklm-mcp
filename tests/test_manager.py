"""
NotebookLM MCP Server Manager — Testes
"""

import json
import sys
import tempfile
from pathlib import Path

# Adicionar raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from cli.config_util import (
    load_servers_config,
    save_servers_config,
    load_app_config,
    SUPPORTED_CLIENTS,
    get_client_config_path,
)
from cli.server_manager import ServerManager


def test_config_load_save():
    """Testa carregar e salvar configuracao."""
    config = load_servers_config()
    assert isinstance(config, dict), "Config deve ser dict"
    assert "servers" in config, "Config deve ter 'servers'"
    print("  [OK] test_config_load_save")


def test_app_config():
    """Testa configuracao do app."""
    config = load_app_config()
    assert isinstance(config, dict), "App config deve ser dict"
    print("  [OK] test_app_config")


def test_supported_clients():
    """Testa clientes suportados."""
    assert len(SUPPORTED_CLIENTS) >= 3, "Deve ter pelo menos 3 clientes"
    assert "Cursor" in SUPPORTED_CLIENTS
    assert "Claude Desktop" in SUPPORTED_CLIENTS
    assert "Antigravity" in SUPPORTED_CLIENTS
    print("  [OK] test_supported_clients")


def test_client_paths():
    """Testa caminhos de configuracao de clientes."""
    for client in SUPPORTED_CLIENTS:
        path = get_client_config_path(client)
        assert path is not None, f"Path para '{client}' nao deve ser None"
    print("  [OK] test_client_paths")


def test_server_manager_init():
    """Testa inicializacao do ServerManager."""
    manager = ServerManager(PROJECT_ROOT)
    assert manager is not None
    assert manager.project_root == PROJECT_ROOT
    print("  [OK] test_server_manager_init")


def test_server_list():
    """Testa listagem de servidores."""
    manager = ServerManager(PROJECT_ROOT)
    servers = manager.list_servers()
    assert isinstance(servers, list), "list_servers deve retornar lista"
    print("  [OK] test_server_list")


def test_add_remove_server():
    """Testa adicionar e remover servidor."""
    manager = ServerManager(PROJECT_ROOT)

    # Salvar estado original
    original = load_servers_config()

    # Adicionar
    test_config = {
        "name": "__test_server__",
        "command": "echo",
        "args": ["test"],
        "transport": "stdio",
        "env": {},
    }
    assert manager.add_server(test_config), "Deve adicionar servidor"

    # Verificar
    info = manager.get_server_info("__test_server__")
    assert info is not None, "Servidor deve existir"
    assert info["command"] == "echo"

    # Remover
    assert manager.remove_server("__test_server__"), "Deve remover servidor"

    # Restaurar
    save_servers_config(original)
    print("  [OK] test_add_remove_server")


def test_get_logs_nonexistent():
    """Testa logs de servidor inexistente."""
    manager = ServerManager(PROJECT_ROOT)
    logs = manager.get_logs("__nonexistent__")
    assert logs is None, "Logs de servidor inexistente devem ser None"
    print("  [OK] test_get_logs_nonexistent")


def main():
    print()
    print("=" * 45)
    print("  NotebookLM MCP Server Manager - Testes")
    print("=" * 45)
    print()

    tests = [
        test_config_load_save,
        test_app_config,
        test_supported_clients,
        test_client_paths,
        test_server_manager_init,
        test_server_list,
        test_add_remove_server,
        test_get_logs_nonexistent,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  [FALHA] {test.__name__}: {e}")
            failed += 1

    print()
    print(f"  Resultado: {passed}/{passed + failed} testes passaram")
    if failed:
        print(f"  {failed} teste(s) falharam!")
        sys.exit(1)
    else:
        print("  Todos os testes passaram!")
    print()


if __name__ == "__main__":
    main()
