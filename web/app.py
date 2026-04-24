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
from skills_extractor.video_processor import VideoProcessor
from skills_extractor.ai_extractor import AIExtractor
from skills_extractor.skill_generator import SkillGenerator
from skills_extractor.installer import SkillInstaller
from skills_extractor.dom_extractor import DOMExtractor

app = Flask(
    __name__,
    template_folder=str(PROJECT_ROOT / "web" / "templates"),
    static_folder=str(PROJECT_ROOT / "web" / "static"),
)
app.config["SECRET_KEY"] = os.urandom(32).hex()


@app.after_request
def add_cors_headers(response):
    """Permite requisições da extensão Chrome (sem origem http://)."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response


@app.route("/api/skills/ingest", methods=["OPTIONS"])
@app.route("/api/skills/extension/ping", methods=["OPTIONS"])
def extension_preflight():
    return '', 204


manager = ServerManager(PROJECT_ROOT)
video_proc = VideoProcessor()
ai_extractor = AIExtractor()
skill_gen = SkillGenerator()
skill_installer = SkillInstaller(PROJECT_ROOT)
guard = SecurityGuard()
dom_extractor = DOMExtractor(PROJECT_ROOT / "skills")

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


# === Skills Extractor API ===

@app.route("/skills")
def skills_page():
    return render_template("skills.html")


@app.route("/api/skills/extract", methods=["POST"])
def api_extract_skills():
    """Pipeline completo: URL -> Transcript -> AI -> Skill files."""
    data = request.get_json()
    urls = data.get("urls", [])
    provider = data.get("provider")

    if not urls:
        return jsonify({"error": "Nenhuma URL fornecida"}), 400

    results = []

    for url in urls:
        url = url.strip()
        if not url:
            continue

        # 1) Transcript
        transcript_data = video_proc.get_transcript(url)
        if "error" in transcript_data:
            results.append({"url": url, "error": transcript_data["error"], "stage": "transcript"})
            continue

        # 2) AI Extraction
        extraction = ai_extractor.extract_skills(
            transcript_data.get("transcript", ""),
            video_title=transcript_data.get("title", ""),
            provider=provider,
        )
        if "error" in extraction:
            results.append({"url": url, "error": extraction["error"], "stage": "ai_extraction"})
            continue

        # 3) Generate skill files
        video_info = {
            "video_id": transcript_data.get("video_id"),
            "title": transcript_data.get("title"),
            "url": url,
            "duration_seconds": transcript_data.get("duration_seconds"),
        }
        generated = skill_gen.generate_all_skills(extraction, video_info)

        results.append({
            "url": url,
            "video_title": transcript_data.get("title"),
            "video_id": transcript_data.get("video_id"),
            "duration": transcript_data.get("duration_seconds"),
            "skills_count": len(generated),
            "skills": generated,
            "summary": extraction.get("video_summary", ""),
            "topics": extraction.get("main_topics", []),
        })

    return jsonify({
        "success": True,
        "results": results,
        "total_videos": len(results),
        "total_skills": sum(r.get("skills_count", 0) for r in results if "error" not in r),
    })


@app.route("/api/skills/transcript", methods=["POST"])
def api_get_transcript():
    """Apenas extrai transcript sem processar com IA."""
    data = request.get_json()
    url = data.get("url", "")
    if not url:
        return jsonify({"error": "URL nao fornecida"}), 400
    result = video_proc.get_transcript(url)
    return jsonify(result)


@app.route("/api/skills", methods=["GET"])
def api_list_skills():
    """Lista todas as skills extraidas."""
    skills = skill_gen.list_skills()
    return jsonify({"skills": skills, "count": len(skills)})


@app.route("/api/skills/<slug>", methods=["GET"])
def api_get_skill(slug):
    """Detalhes de uma skill."""
    skill = skill_gen.get_skill(slug)
    if not skill:
        return jsonify({"error": "Skill nao encontrada"}), 404
    return jsonify(skill)


@app.route("/api/skills/<slug>", methods=["DELETE"])
def api_delete_skill(slug):
    """Remove uma skill."""
    if skill_gen.delete_skill(slug):
        return jsonify({"success": True, "message": f"Skill '{slug}' removida"})
    return jsonify({"error": "Skill nao encontrada"}), 404


@app.route("/api/skills/install", methods=["POST"])
def api_install_skills():
    """Instala o servidor MCP de skills em um cliente."""
    data = request.get_json()
    client = data.get("client", "")
    result = skill_installer.install_to_client(client)
    status = 200 if result.get("success") else 400
    return jsonify(result), status


@app.route("/api/skills/install/status", methods=["GET"])
def api_install_status():
    """Status de instalacao nos clientes."""
    return jsonify({"clients": skill_installer.get_install_status()})


@app.route("/api/skills/ai/status", methods=["GET"])
def api_ai_status():
    """Status das APIs de IA configuradas."""
    return jsonify(ai_extractor.get_status())


@app.route("/api/skills/ai/configure", methods=["POST"])
def api_configure_ai():
    """Configura API key de IA."""
    data = request.get_json()
    provider = data.get("provider")
    api_key = data.get("api_key")
    model = data.get("model")
    if not provider or not api_key:
        return jsonify({"error": "provider e api_key sao obrigatorios"}), 400
    ai_extractor.set_api_key(provider, api_key, model=model)
    return jsonify({"success": True, "message": f"API key {provider} configurada"})


@app.route("/api/skills/config/snippet", methods=["GET"])
def api_config_snippet():
    """Retorna snippet de config MCP para copia manual."""
    return jsonify(skill_installer.generate_config_snippet())


# === Extension Bridge (Chrome Extension → Flask) ===

@app.route("/api/skills/extension/ping", methods=["GET"])
def api_extension_ping():
    """Endpoint de health check para a extensão Chrome verificar se o Flask está online."""
    return jsonify({"status": "online", "version": "2.0.0", "service": "NotebookLM MCP"})


@app.route("/api/skills/ingest", methods=["POST"])
def api_ingest_from_extension():
    """
    Recebe metadados extraídos pela extensão Chrome do YouTube (sem LLM).
    Gera skill estruturada e opcionalmente adiciona URL ao NotebookLM.
    """
    data = request.get_json()
    if not data or not data.get("video_id"):
        return jsonify({"error": "video_id obrigatório"}), 400

    notebook_id = data.get("notebook_id") or app.config.get("DEFAULT_NOTEBOOK_ID", "")

    # Adicionar ao NotebookLM via CLI (se tiver notebook configurado)
    notebooklm_added = False
    notebooklm_error = None
    if notebook_id:
        import subprocess
        url = data.get("url", "")
        try:
            result = subprocess.run(
                ["nlm", "source", "add", notebook_id, "--url", url, "--wait"],
                capture_output=True, text=True, timeout=60,
            )
            notebooklm_added = result.returncode == 0
            if not notebooklm_added:
                notebooklm_error = result.stderr.strip() or result.stdout.strip()
        except Exception as e:
            notebooklm_error = str(e)

    data["notebooklm_added"] = notebooklm_added

    # Gerar skill sem LLM
    try:
        skill = dom_extractor.ingest(data)
    except Exception as e:
        return jsonify({"error": f"Erro ao gerar skill: {str(e)}"}), 500

    return jsonify({
        "success": True,
        "skill": skill,
        "notebooklm_added": notebooklm_added,
        "notebooklm_error": notebooklm_error,
        "already_existed": skill.get("already_existed", False),
        "message": (
            f"Skill '{skill['name']}' já existia." if skill.get("already_existed")
            else f"Skill '{skill['name']}' criada com sucesso!"
        ),
    })


@app.route("/api/skills/dom", methods=["GET"])
def api_list_dom_skills():
    """Lista skills geradas pela extensão (sem LLM)."""
    skills = dom_extractor.list_skills()
    return jsonify({"skills": skills, "count": len(skills)})


@app.route("/api/skills/dom/<slug>", methods=["DELETE"])
def api_delete_dom_skill(slug):
    if dom_extractor.delete_skill(slug):
        return jsonify({"success": True})
    return jsonify({"error": "Skill não encontrada"}), 404


# === Health ===

@app.route("/api/health", methods=["GET"])
def api_health():
    servers = manager.list_servers()
    running = sum(1 for s in servers if s.get("running"))
    return jsonify({
        "status": "ok",
        "version": "1.2.0",
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
        threaded=True,
    )


if __name__ == "__main__":
    main()
