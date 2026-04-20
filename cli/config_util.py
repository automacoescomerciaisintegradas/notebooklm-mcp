"""
NotebookLM MCP Server Manager — Utilitarios de Configuracao
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

SUPPORTED_CLIENTS = ["Cursor", "Claude Desktop", "Antigravity"]

DEFAULT_CONFIG = {
    "servers": {},
    "settings": {
        "auto_start": False,
        "log_level": "INFO",
        "check_updates": True,
        "language": "pt-br",
    },
}


def get_config_dir() -> Path:
    """Retorna o diretorio de configuracao do projeto."""
    return Path(__file__).parent.parent / "config"


def get_logs_dir() -> Path:
    """Retorna o diretorio de logs."""
    return Path(__file__).parent.parent / "logs"


def load_servers_config() -> dict:
    """Carrega configuracao de servidores."""
    config_path = get_config_dir() / "servers.json"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"servers": {}}


def save_servers_config(config: dict):
    """Salva configuracao de servidores."""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "servers.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def load_app_config() -> dict:
    """Carrega configuracao do aplicativo."""
    config_path = get_config_dir() / "app_config.json"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_CONFIG.get("settings", {})


def save_app_config(config: dict):
    """Salva configuracao do aplicativo."""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "app_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_client_config_path(client: str) -> Optional[Path]:
    """Retorna o caminho do arquivo de configuracao MCP do cliente."""
    home = Path.home()

    paths = {
        "Cursor": home / ".cursor" / "mcp.json",
        "Claude Desktop": (
            home / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
            if sys.platform == "win32"
            else home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        ),
        "Antigravity": home / ".antigravity" / "mcp.json",
    }

    return paths.get(client)


def read_client_config(client: str) -> dict:
    """Le configuracao MCP de um cliente."""
    path = get_client_config_path(client)
    if path and path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"mcpServers": {}}


def write_client_config(client: str, config: dict) -> bool:
    """Escreve configuracao MCP em um cliente."""
    path = get_client_config_path(client)
    if not path:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    return True


def merge_server_to_client(client: str, server_name: str, server_config: dict) -> bool:
    """Adiciona/atualiza um servidor na config de um cliente."""
    config = read_client_config(client)
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    config["mcpServers"][server_name] = {
        "command": server_config.get("command", ""),
        "args": server_config.get("args", []),
        "env": server_config.get("env", {}),
    }
    return write_client_config(client, config)


def remove_server_from_client(client: str, server_name: str) -> bool:
    """Remove um servidor da config de um cliente."""
    config = read_client_config(client)
    if "mcpServers" in config and server_name in config["mcpServers"]:
        del config["mcpServers"][server_name]
        return write_client_config(client, config)
    return False
