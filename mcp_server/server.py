"""
MCP Server — Wrapper principal do NotebookLM MCP
Gerencia comunicacao bidirecional via stdin/stdout (stdio transport).
"""

import json
import subprocess
import sys
import os
from pathlib import Path
from typing import Optional


class MCPServer:
    """Wrapper para comunicacao com o servidor MCP NotebookLM."""

    def __init__(self, command: str = "nlm", args: list = None):
        self.command = command
        self.args = args or ["serve"]
        self.process: Optional[subprocess.Popen] = None

    def start(self) -> bool:
        """Inicia o servidor MCP."""
        try:
            self.process = subprocess.Popen(
                [self.command] + self.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=os.environ.copy(),
            )
            return True
        except Exception as e:
            print(f"[ERRO] Falha ao iniciar MCP server: {e}", file=sys.stderr)
            return False

    def send_request(self, method: str, params: dict = None) -> Optional[dict]:
        """Envia uma requisicao JSON-RPC para o servidor MCP."""
        if not self.process or self.process.poll() is not None:
            return None

        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {},
        }

        try:
            request_str = json.dumps(request) + "\n"
            self.process.stdin.write(request_str)
            self.process.stdin.flush()

            response_line = self.process.stdout.readline()
            if response_line:
                return json.loads(response_line)
        except Exception as e:
            print(f"[ERRO] Comunicacao com MCP: {e}", file=sys.stderr)

        return None

    def stop(self):
        """Para o servidor MCP."""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

    @property
    def is_running(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
