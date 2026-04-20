"""
Skills Extractor — MCP Skill Server
Servidor MCP que expoe skills extraidas como ferramentas.
Comunicacao via JSON-RPC stdio (MCP Protocol).

(c) Automacoes Comerciais Integradas 2026
"""

import json
import sys
import importlib.util
from pathlib import Path


class MCPSkillServer:
    """Servidor MCP que serve skills extraidas como ferramentas."""

    def __init__(self, skills_dir: Path = None):
        self.skills_dir = skills_dir or Path(__file__).parent.parent / "skills"
        self.tools = {}
        self.handlers = {}
        self._load_all_skills()

    def _load_all_skills(self):
        """Carrega todas as skills disponiveis."""
        for skill_py in self.skills_dir.glob("*/skill.py"):
            try:
                slug = skill_py.parent.name
                spec = importlib.util.spec_from_file_location(f"skill_{slug}", skill_py)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if hasattr(module, "TOOLS"):
                    for tool in module.TOOLS:
                        tool_name = tool["name"]
                        self.tools[tool_name] = tool
                        self.handlers[tool_name] = module.handle_tool_call

            except Exception as e:
                print(f"[WARN] Erro ao carregar skill {skill_py}: {e}", file=sys.stderr)

    def get_tools_list(self) -> list[dict]:
        """Retorna lista de ferramentas MCP disponiveis."""
        return list(self.tools.values())

    def handle_request(self, request: dict) -> dict:
        """Processa uma requisicao JSON-RPC."""
        method = request.get("method", "")
        req_id = request.get("id")
        params = request.get("params", {})

        if method == "initialize":
            return self._response(req_id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": True}},
                "serverInfo": {
                    "name": "skills-extractor-mcp",
                    "version": "1.2.0",
                },
            })

        elif method == "tools/list":
            return self._response(req_id, {"tools": self.get_tools_list()})

        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})

            handler = self.handlers.get(tool_name)
            if not handler:
                return self._error(req_id, -32601, f"Tool nao encontrada: {tool_name}")

            try:
                result = handler(tool_name, arguments)
                return self._response(req_id, {
                    "content": [{"type": "text", "text": result}],
                    "isError": False,
                })
            except Exception as e:
                return self._response(req_id, {
                    "content": [{"type": "text", "text": f"Erro: {str(e)}"}],
                    "isError": True,
                })

        elif method == "notifications/initialized":
            return None  # Notificacao, sem resposta

        else:
            return self._error(req_id, -32601, f"Metodo desconhecido: {method}")

    def _response(self, req_id, result: dict) -> dict:
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    def _error(self, req_id, code: int, message: str) -> dict:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}

    def run_stdio(self):
        """Loop principal: le JSON-RPC de stdin, escreve em stdout."""
        print(f"[skills-extractor-mcp] Carregadas {len(self.tools)} ferramentas", file=sys.stderr)

        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                request = json.loads(line)
                response = self.handle_request(request)
                if response:
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
            except json.JSONDecodeError:
                error = self._error(None, -32700, "JSON invalido")
                sys.stdout.write(json.dumps(error) + "\n")
                sys.stdout.flush()


def main():
    server = MCPSkillServer()
    server.run_stdio()


if __name__ == "__main__":
    main()
