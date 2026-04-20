"""
NotebookLM MCP Skill — Acesso programático ao Google NotebookLM
Integração com Antigravity, Claude Code, Gemini e CLI
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Optional, Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class NotebookLMClient:
    """Cliente Python para NotebookLM via CLI"""

    def __init__(self, profile: Optional[str] = None):
        """
        Inicializar cliente NotebookLM

        Args:
            profile: Nome do perfil Google (ex: 'work', 'personal')
        """
        self.profile = profile
        self.check_installed()

    def check_installed(self) -> bool:
        """Verificar se notebooklm-mcp-cli está instalado"""
        try:
            result = subprocess.run(
                ["nlm", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"NotebookLM CLI: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            logger.error(
                "notebooklm-mcp-cli não instalado. "
                "Execute: uv tool install notebooklm-mcp-cli"
            )
            return False

    def _run_cmd(self, cmd: List[str], json_output: bool = False) -> Any:
        """Executar comando nlm"""
        if self.profile:
            cmd.extend(["--profile", self.profile])

        if json_output:
            cmd.append("--json")

        logger.debug(f"Executando: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"Erro: {result.stderr}")
            raise RuntimeError(f"Comando falhou: {result.stderr}")

        if json_output:
            return json.loads(result.stdout)
        return result.stdout.strip()

    # ==================== NOTEBOOKS ====================

    def list_notebooks(self) -> List[Dict]:
        """Listar todos os notebooks"""
        return self._run_cmd(["nlm", "notebook", "list"], json_output=True)

    def create_notebook(self, name: str, description: str = "") -> Dict:
        """Criar novo notebook"""
        cmd = ["nlm", "notebook", "create", name]
        if description:
            cmd.extend(["--description", description])
        return self._run_cmd(cmd, json_output=True)

    def delete_notebook(self, notebook: str) -> bool:
        """Deletar notebook"""
        self._run_cmd(["nlm", "notebook", "delete", notebook, "--confirm"])
        return True

    def query_notebook(self, notebook: str, question: str) -> str:
        """Fazer pergunta ao notebook"""
        return self._run_cmd(
            ["nlm", "notebook", "query", notebook, question]
        )

    # ==================== FONTES ====================

    def add_source_url(self, notebook: str, url: str) -> Dict:
        """Adicionar fonte via URL"""
        return self._run_cmd(
            ["nlm", "source", "add", notebook, "--url", url],
            json_output=True
        )

    def add_source_text(self, notebook: str, text: str) -> Dict:
        """Adicionar fonte via texto"""
        return self._run_cmd(
            ["nlm", "source", "add", notebook, "--text", text],
            json_output=True
        )

    def add_source_file(self, notebook: str, file_path: str) -> Dict:
        """Adicionar fonte via arquivo"""
        return self._run_cmd(
            ["nlm", "source", "add", notebook, "--file", file_path],
            json_output=True
        )

    def sync_drive_sources(self, notebook: str) -> Dict:
        """Sincronizar fontes do Google Drive"""
        return self._run_cmd(
            ["nlm", "source", "sync", notebook],
            json_output=True
        )

    # ==================== STUDIO (GERAÇÃO DE CONTEÚDO) ====================

    def create_audio(
        self,
        notebook: str,
        format: str = "standard",
        confirm: bool = True
    ) -> Dict:
        """Gerar áudio/podcast"""
        cmd = ["nlm", "audio", "create", notebook]
        if format:
            cmd.extend(["--format", format])
        if confirm:
            cmd.append("--confirm")
        return self._run_cmd(cmd, json_output=True)

    def create_video(
        self,
        notebook: str,
        style: str = "classic",
        confirm: bool = True
    ) -> Dict:
        """Gerar vídeo"""
        cmd = ["nlm", "studio", "create", notebook, "--type", "video"]
        if style:
            cmd.extend(["--style", style])
        if confirm:
            cmd.append("--confirm")
        return self._run_cmd(cmd, json_output=True)

    def create_slides(
        self,
        notebook: str,
        style: str = "professional",
        confirm: bool = True
    ) -> Dict:
        """Gerar apresentação"""
        cmd = ["nlm", "studio", "create", notebook, "--type", "slides"]
        if style:
            cmd.extend(["--style", style])
        if confirm:
            cmd.append("--confirm")
        return self._run_cmd(cmd, json_output=True)

    def revise_slides(self, notebook: str, revision: str = "") -> Dict:
        """Revisar deck de slides"""
        cmd = ["nlm", "slides", "revise", notebook]
        if revision:
            cmd.extend(["--revision", revision])
        return self._run_cmd(cmd, json_output=True)

    # ==================== DOWNLOAD ====================

    def download_artifact(
        self,
        notebook: str,
        artifact_id: str,
        output_path: str = "./"
    ) -> str:
        """Baixar artefato gerado (áudio, vídeo, etc)"""
        cmd = [
            "nlm", "download", "audio", notebook, artifact_id,
            "--output", output_path
        ]
        return self._run_cmd(cmd)

    # ==================== COMPARTILHAMENTO ====================

    def share_public(self, notebook: str) -> Dict:
        """Publicar notebook (link público)"""
        return self._run_cmd(
            ["nlm", "share", "public", notebook],
            json_output=True
        )

    def share_invite(
        self,
        notebook: str,
        email: str,
        role: str = "viewer"
    ) -> Dict:
        """Convidar usuário para notebook"""
        cmd = ["nlm", "share", "invite", notebook, email]
        if role:
            cmd.extend(["--role", role])
        return self._run_cmd(cmd, json_output=True)

    def unshare(self, notebook: str, email: str) -> bool:
        """Revogar acesso a notebook"""
        self._run_cmd(["nlm", "share", "revoke", notebook, email])
        return True

    # ==================== PESQUISA ====================

    def research_start(self, query: str, depth: str = "standard") -> Dict:
        """Iniciar pesquisa web com IA"""
        cmd = ["nlm", "research", "start", query]
        if depth:
            cmd.extend(["--depth", depth])
        return self._run_cmd(cmd, json_output=True)

    # ==================== CROSS-NOTEBOOK ====================

    def cross_notebook_query(
        self,
        notebooks: List[str],
        question: str
    ) -> Dict:
        """Perguntar a múltiplos notebooks"""
        cmd = ["nlm", "cross", "query"] + notebooks + [question]
        return self._run_cmd(cmd, json_output=True)

    # ==================== BATCH ====================

    def batch_create(self, names: List[str]) -> List[Dict]:
        """Criar múltiplos notebooks em lote"""
        cmd = ["nlm", "batch", "create"] + names
        return self._run_cmd(cmd, json_output=True)

    def batch_query(self, notebook: str, questions: List[str]) -> List[str]:
        """Fazer múltiplas perguntas em lote"""
        cmd = ["nlm", "batch", "query", notebook] + questions
        return self._run_cmd(cmd, json_output=True)

    # ==================== TAGGING ====================

    def tag_add(self, notebook: str, tag: str) -> Dict:
        """Adicionar tag a notebook"""
        return self._run_cmd(
            ["nlm", "tag", "add", notebook, tag],
            json_output=True
        )

    def tag_list(self) -> List[str]:
        """Listar todas as tags"""
        return self._run_cmd(
            ["nlm", "tag", "list"],
            json_output=True
        )

    def tag_select(self, tag: str) -> List[Dict]:
        """Selecionar notebooks por tag"""
        return self._run_cmd(
            ["nlm", "tag", "select", tag],
            json_output=True
        )

    # ==================== PIPELINES ====================

    def pipeline_run(self, pipeline_name: str, params: Dict = None) -> Dict:
        """Rodar pipeline"""
        cmd = ["nlm", "pipeline", "run", pipeline_name]
        if params:
            cmd.extend(["--params", json.dumps(params)])
        return self._run_cmd(cmd, json_output=True)

    def pipeline_list(self) -> List[Dict]:
        """Listar pipelines"""
        return self._run_cmd(
            ["nlm", "pipeline", "list"],
            json_output=True
        )


# ==================== SETUP AUTOMÁTICO ====================

def setup_authentication(profile: str = "default") -> bool:
    """Setup de autenticação interativo"""
    logger.info(f"Configurando autenticação (perfil: {profile})...")
    try:
        subprocess.run(
            ["nlm", "login", "--profile", profile],
            check=True
        )
        logger.info("✅ Autenticação concluída!")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erro na autenticação: {e}")
        return False


def setup_mcp_for_tool(tool: str) -> bool:
    """Configurar MCP para ferramenta específica"""
    logger.info(f"Configurando MCP para {tool}...")
    try:
        subprocess.run(
            ["nlm", "setup", "add", tool],
            check=True
        )
        logger.info(f"✅ MCP configurado para {tool}!")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erro ao configurar MCP: {e}")
        return False


def diagnose_system() -> Dict[str, bool]:
    """Diagnosticar instalação e autenticação"""
    logger.info("Executando diagnóstico...")
    try:
        result = subprocess.run(
            ["nlm", "doctor"],
            capture_output=True,
            text=True,
            timeout=10
        )
        # Parse output and return status
        return {"status": "ok" if result.returncode == 0 else "error"}
    except Exception as e:
        logger.error(f"Erro no diagnóstico: {e}")
        return {"status": "error"}


# ==================== EXEMPLOS ====================

def example_create_and_query():
    """Exemplo: Criar notebook e fazer pergunta"""
    client = NotebookLMClient()

    # Criar
    nb = client.create_notebook(
        "Test Research",
        "Pesquisa automática"
    )
    nb_id = nb['id']
    logger.info(f"✅ Notebook criado: {nb_id}")

    # Adicionar fonte
    client.add_source_url(
        nb_id,
        "https://arxiv.org/list/cs.AI/recent"
    )
    logger.info("✅ Fonte adicionada")

    # Perguntar
    response = client.query_notebook(
        nb_id,
        "Quais são as tendências principais?"
    )
    logger.info(f"Resposta: {response}")

    return nb_id


def example_research_and_podcast():
    """Exemplo: Pesquisa → Notebook → Áudio"""
    client = NotebookLMClient()

    # Pesquisar
    logger.info("🔍 Pesquisando...")
    research = client.research_start("AI trends 2026", depth="comprehensive")

    # Criar notebook
    logger.info("📚 Criando notebook...")
    nb = client.create_notebook("AI Trends Research 2026")
    nb_id = nb['id']

    # Adicionar fontes
    logger.info("📎 Adicionando fontes...")
    if 'sources' in research:
        for source in research['sources'][:5]:  # Limitar a 5
            try:
                client.add_source_url(nb_id, source.get('url'))
            except Exception as e:
                logger.warning(f"Erro ao adicionar fonte: {e}")

    # Gerar áudio
    logger.info("🎙️ Gerando áudio...")
    audio = client.create_audio(nb_id, format="deep-dive")

    logger.info(f"✅ Concluído! Áudio: {audio.get('id')}")
    return nb_id, audio


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Exemplo
    logger.info("Iniciando exemplo...")
    try:
        example_create_and_query()
    except Exception as e:
        logger.error(f"Erro: {e}")
