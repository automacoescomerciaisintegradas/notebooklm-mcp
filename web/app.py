"""
NotebookLM MCP Server Manager — Web Interface
Servidor Flask com API REST e dashboard web.

Acesse: http://localhost:5117

(c) Automacoes Comerciais Integradas 2026
"""

import sys
import os
import json
import webbrowser
import threading
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, render_template, jsonify, request, Response
from cli.server_manager import ServerManager
from cli.config_util import (
    load_servers_config,
    save_servers_config,
    load_app_config,
    save_app_config,
    SUPPORTED_CLIENTS,
    get_client_config_path,
)
from core.security_guard import SecurityGuard

app = Flask(
    __name__,
    template_folder=str(PROJECT_ROOT / "web" / "templates"),
    static_folder=str(PROJECT_ROOT / "web" / "static"),
)
app.config["SECRET_KEY"] = os.urandom(32).hex()

manager = ServerManager(PROJECT_ROOT)
guard = SecurityGuard()

PORT = 5117


# === Pages ===

@app.route("/")
def index():
    return render_template("index.html")


# === API REST ===

@app.route("/api/servers", methods=["GET"])
def api_list_servers():
    servers = manager.list_servers()
    return jsonify({"servers": servers, "count": len(servers)})


@app.route("/api/servers", methods=["POST"])
def api_add_server():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Nome e obrigatorio"}), 400

    # SecurityGuard — validar comando
    command = data.get("command", "")
    check = guard.validate_command(command)
    if not check.is_safe:
        return jsonify({
            "error": "Comando bloqueado pelo SecurityGuard",
            "violation": check.violation.to_dict(),
        }), 403

    server_config = {
        "name": data["name"],
        "command": command,
        "transport": data.get("transport", "stdio"),
        "args": data.get("args", []),
        "env": data.get("env", {}),
    }
    port = data.get("port")
    if port:
        try:
            server_config["port"] = int(port)
        except ValueError:
            return jsonify({"error": "Porta invalida"}), 400

    if manager.add_server(server_config):
        return jsonify({"success": True, "message": f"Servidor '{data['name']}' adicionado"})
    return jsonify({"error": "Falha ao adicionar servidor"}), 500


@app.route("/api/servers/<name>", methods=["DELETE"])
def api_remove_server(name):
    if manager.remove_server(name):
        return jsonify({"success": True, "message": f"Servidor '{name}' removido"})
    return jsonify({"error": f"Servidor '{name}' nao encontrado"}), 404


@app.route("/api/servers/<name>/start", methods=["POST"])
def api_start_server(name):
    if manager.start_server(name):
        return jsonify({"success": True, "message": f"Servidor '{name}' iniciado"})
    return jsonify({"error": f"Falha ao iniciar '{name}'"}), 500


@app.route("/api/servers/<name>/stop", methods=["POST"])
def api_stop_server(name):
    if manager.stop_server(name):
        return jsonify({"success": True, "message": f"Servidor '{name}' parado"})
    return jsonify({"error": f"Falha ao parar '{name}'"}), 500


@app.route("/api/servers/<name>/restart", methods=["POST"])
def api_restart_server(name):
    manager.stop_server(name)
    if manager.start_server(name):
        return jsonify({"success": True, "message": f"Servidor '{name}' reiniciado"})
    return jsonify({"error": f"Falha ao reiniciar '{name}'"}), 500


@app.route("/api/servers/<name>/info", methods=["GET"])
def api_server_info(name):
    info = manager.get_server_info(name)
    if info:
        return jsonify(info)
    return jsonify({"error": f"Servidor '{name}' nao encontrado"}), 404


@app.route("/api/servers/<name>/logs", methods=["GET"])
def api_server_logs(name):
    lines = request.args.get("lines", 100, type=int)
    logs = manager.get_logs(name, lines)
    return jsonify({"name": name, "logs": logs or "", "has_logs": logs is not None})


@app.route("/api/servers/<name>/logs/clear", methods=["POST"])
def api_clear_logs(name):
    if manager.clear_logs(name):
        return jsonify({"success": True})
    return jsonify({"error": "Nenhum log encontrado"}), 404


# === Clients ===

@app.route("/api/clients", methods=["GET"])
def api_list_clients():
    clients = []
    for c in SUPPORTED_CLIENTS:
        path = get_client_config_path(c)
        clients.append({
            "name": c,
            "config_path": str(path) if path else None,
            "exists": path.exists() if path else False,
        })
    return jsonify({"clients": clients})


@app.route("/api/clients/<client>/configure", methods=["POST"])
def api_configure_client(client):
    if client not in SUPPORTED_CLIENTS:
        return jsonify({"error": f"Cliente '{client}' nao suportado"}), 400
    if manager.configure_client(client):
        return jsonify({"success": True, "message": f"Servidores exportados para '{client}'"})
    return jsonify({"error": f"Falha ao configurar '{client}'"}), 500


# === Security ===

@app.route("/api/security/status", methods=["GET"])
def api_security_status():
    return jsonify({
        "enabled": guard.enabled,
        "pattern_count": guard.pattern_count,
        "violation_count": guard.violation_count,
        "summary": guard.get_violations_summary(),
    })


@app.route("/api/security/validate", methods=["POST"])
def api_security_validate():
    data = request.get_json()
    command = data.get("command", "")
    result = guard.validate_command(command)
    resp = {"is_safe": result.is_safe, "command": command}
    if not result.is_safe:
        resp["violation"] = result.violation.to_dict()
    return jsonify(resp)


# === Config ===

@app.route("/api/config", methods=["GET"])
def api_get_config():
    return jsonify(load_app_config())


@app.route("/api/config", methods=["PUT"])
def api_update_config():
    data = request.get_json()
    if data:
        save_app_config(data)
        return jsonify({"success": True})
    return jsonify({"error": "Dados invalidos"}), 400


# === Health ===

@app.route("/api/health", methods=["GET"])
def api_health():
    servers = manager.list_servers()
    running = sum(1 for s in servers if s.get("running"))
    return jsonify({
        "status": "ok",
        "version": "1.1.0",
        "timestamp": datetime.now().isoformat(),
        "servers_total": len(servers),
        "servers_running": running,
        "security_enabled": guard.enabled,
        "security_patterns": guard.pattern_count,
    })


def open_browser():
    webbrowser.open(f"http://localhost:{PORT}")


def main():
    print()
    print("=" * 55)
    print("  NotebookLM MCP Server Manager — Web Interface")
    print(f"  http://localhost:{PORT}")
    print("  (c) Automacoes Comerciais Integradas 2026")
    print("=" * 55)
    print()

    # Abrir navegador apos 1.5s
    threading.Timer(1.5, open_browser).start()

    app.run(
        host="127.0.0.1",
        port=PORT,
        debug=False,
        use_reloader=False,
    )


if __name__ == "__main__":
    main()
