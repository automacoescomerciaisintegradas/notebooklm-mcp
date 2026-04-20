"""
NotebookLM MCP Server Manager — Gerenciador de Servidores
"""

import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from cli.config_util import (
    load_servers_config,
    save_servers_config,
    get_logs_dir,
    merge_server_to_client,
    SUPPORTED_CLIENTS,
)


class ServerManager:
    """Gerencia ciclo de vida de servidores MCP."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.processes: dict[str, subprocess.Popen] = {}
        self.logs_dir = get_logs_dir()
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def list_servers(self) -> list[dict]:
        """Lista todos os servidores configurados com status."""
        config = load_servers_config()
        servers = []
        for name, srv in config.get("servers", {}).items():
            running = name in self.processes and self.processes[name].poll() is None
            pid = self.processes[name].pid if running else None
            servers.append({
                "name": name,
                "command": srv.get("command", ""),
                "transport": srv.get("transport", "stdio"),
                "port": srv.get("port"),
                "running": running,
                "pid": pid,
            })
        return servers

    def add_server(self, server_config: dict) -> bool:
        """Adiciona um servidor a configuracao."""
        name = server_config.get("name")
        if not name:
            return False
        config = load_servers_config()
        config.setdefault("servers", {})[name] = server_config
        save_servers_config(config)
        return True

    def remove_server(self, name: str) -> bool:
        """Remove um servidor da configuracao."""
        config = load_servers_config()
        if name in config.get("servers", {}):
            self.stop_server(name)
            del config["servers"][name]
            save_servers_config(config)
            return True
        return False

    def start_server(self, name: str) -> bool:
        """Inicia um servidor MCP."""
        config = load_servers_config()
        srv = config.get("servers", {}).get(name)
        if not srv:
            return False

        if name in self.processes and self.processes[name].poll() is None:
            return True  # Ja rodando

        command = srv.get("command", "")
        args = srv.get("args", [])
        env_vars = srv.get("env", {})

        env = os.environ.copy()
        env.update(env_vars)

        log_file = self.logs_dir / f"{name}.log"

        try:
            cmd_parts = [command] + args
            with open(log_file, "a", encoding="utf-8") as lf:
                lf.write(f"\n--- Servidor iniciado: {datetime.now().isoformat()} ---\n")
                process = subprocess.Popen(
                    cmd_parts,
                    stdout=lf,
                    stderr=subprocess.STDOUT,
                    env=env,
                    cwd=str(self.project_root),
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                )
            self.processes[name] = process
            return True
        except Exception as e:
            with open(log_file, "a", encoding="utf-8") as lf:
                lf.write(f"[ERRO] Falha ao iniciar: {e}\n")
            return False

    def stop_server(self, name: str) -> bool:
        """Para um servidor MCP."""
        if name not in self.processes:
            return False

        process = self.processes[name]
        if process.poll() is not None:
            del self.processes[name]
            return True

        try:
            if sys.platform == "win32":
                process.terminate()
            else:
                os.kill(process.pid, signal.SIGTERM)

            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)

            del self.processes[name]

            log_file = self.logs_dir / f"{name}.log"
            with open(log_file, "a", encoding="utf-8") as lf:
                lf.write(f"--- Servidor parado: {datetime.now().isoformat()} ---\n")

            return True
        except Exception:
            return False

    def get_logs(self, name: str, lines: int = 100) -> Optional[str]:
        """Retorna as ultimas N linhas de log de um servidor."""
        log_file = self.logs_dir / f"{name}.log"
        if not log_file.exists():
            return None
        with open(log_file, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()
        return "".join(all_lines[-lines:])

    def clear_logs(self, name: str) -> bool:
        """Limpa logs de um servidor."""
        log_file = self.logs_dir / f"{name}.log"
        if log_file.exists():
            log_file.write_text("", encoding="utf-8")
            return True
        return False

    def configure_client(self, client: str) -> bool:
        """Configura todos os servidores em um cliente."""
        config = load_servers_config()
        success = True
        for name, srv in config.get("servers", {}).items():
            if not merge_server_to_client(client, name, srv):
                success = False
        return success

    def get_server_info(self, name: str) -> Optional[dict]:
        """Retorna informacoes detalhadas de um servidor."""
        config = load_servers_config()
        srv = config.get("servers", {}).get(name)
        if not srv:
            return None
        running = name in self.processes and self.processes[name].poll() is None
        return {
            **srv,
            "running": running,
            "pid": self.processes[name].pid if running else None,
        }

    def stop_all(self):
        """Para todos os servidores em execucao."""
        for name in list(self.processes.keys()):
            self.stop_server(name)
