"""
Skills Extractor — Installer
Instala skills extraidas nos clientes MCP (Claude Desktop, Cursor, Antigravity).
Registra o servidor MCP de skills na configuracao do cliente.

(c) Automacoes Comerciais Integradas 2026
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from cli.config_util import get_client_config_path, SUPPORTED_CLIENTS


class SkillInstaller:
    """Instala o servidor MCP de skills nos clientes."""

    SERVER_NAME = "skills-extractor"

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.server_script = self.project_root / "skills_extractor" / "mcp_skill_server.py"

    def install_to_client(self, client: str) -> dict:
        """
        Instala o skills-extractor MCP server em um cliente.
        client: 'Cursor', 'Claude Desktop', 'Antigravity'
        """
        if client not in SUPPORTED_CLIENTS:
            return {"success": False, "error": f"Cliente nao suportado: {client}. Use: {SUPPORTED_CLIENTS}"}

        config_path = get_client_config_path(client)
        if not config_path:
            return {"success": False, "error": f"Caminho de config nao encontrado para {client}"}

        config_path = Path(config_path)

        # Criar diretorio se nao existir
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Carregar config existente
        config = {}
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except Exception:
                config = {}

        # Adicionar servidor MCP
        config.setdefault("mcpServers", {})
        config["mcpServers"][self.SERVER_NAME] = {
            "command": "python",
            "args": [str(self.server_script)],
            "cwd": str(self.project_root),
        }

        # Salvar
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        return {
            "success": True,
            "message": f"Skills Extractor instalado em {client}",
            "config_path": str(config_path),
            "server_name": self.SERVER_NAME,
        }

    def uninstall_from_client(self, client: str) -> dict:
        """Remove o skills-extractor de um cliente."""
        config_path = get_client_config_path(client)
        if not config_path:
            return {"success": False, "error": f"Config nao encontrada para {client}"}

        config_path = Path(config_path)
        if not config_path.exists():
            return {"success": False, "error": "Arquivo de config nao existe"}

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        servers = config.get("mcpServers", {})
        if self.SERVER_NAME in servers:
            del servers[self.SERVER_NAME]
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return {"success": True, "message": f"Skills Extractor removido de {client}"}

        return {"success": False, "error": "Skills Extractor nao estava instalado"}

    def get_install_status(self) -> list[dict]:
        """Retorna status de instalacao em cada cliente."""
        status = []
        for client in SUPPORTED_CLIENTS:
            config_path = get_client_config_path(client)
            installed = False

            if config_path and Path(config_path).exists():
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        config = json.load(f)
                    installed = self.SERVER_NAME in config.get("mcpServers", {})
                except Exception:
                    pass

            status.append({
                "client": client,
                "installed": installed,
                "config_path": str(config_path) if config_path else None,
            })

        return status

    def generate_config_snippet(self) -> dict:
        """Gera snippet de config MCP para copia manual."""
        return {
            self.SERVER_NAME: {
                "command": "python",
                "args": [str(self.server_script)],
                "cwd": str(self.project_root),
            }
        }
