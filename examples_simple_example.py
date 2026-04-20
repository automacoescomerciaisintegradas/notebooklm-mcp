#!/usr/bin/env python3
"""
simple_example.py — Exemplo Simples de Uso

Cria um notebook, adiciona fontes e faz uma pergunta.

Uso:
    python simple_example.py
    python simple_example.py --profile work
"""

from notebooklm_mcp import NotebookLMClient
import argparse
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main(profile="default"):
    logger.info("🚀 Iniciando NotebookLM...")

    # Inicializar cliente
    client = NotebookLMClient(profile=profile)

    # 1. Criar notebook
    logger.info("📚 Criando notebook...")
    notebook = client.create_notebook(
        "Test Notebook",
        "Notebook de teste para demonstração"
    )
    notebook_id = notebook['id']
    logger.info(f"✅ Notebook criado: {notebook_id}")

    # 2. Adicionar fonte (URL)
    logger.info("📎 Adicionando fonte...")
    try:
        source = client.add_source_url(
            notebook_id,
            "https://en.wikipedia.org/wiki/Artificial_intelligence"
        )
        logger.info(f"✅ Fonte adicionada: {source}")
    except Exception as e:
        logger.warning(f"⚠️  Erro ao adicionar fonte: {e}")

    # 3. Adicionar fonte (texto)
    logger.info("📝 Adicionando texto...")
    try:
        source_text = client.add_source_text(
            notebook_id,
            "AI is transforming industries worldwide in 2026."
        )
        logger.info(f"✅ Texto adicionado")
    except Exception as e:
        logger.warning(f"⚠️  Erro ao adicionar texto: {e}")

    # 4. Fazer pergunta
    logger.info("❓ Fazendo pergunta...")
    try:
        response = client.query_notebook(
            notebook_id,
            "O que é inteligência artificial?"
        )
        logger.info(f"✅ Resposta:\n\n{response}\n")
    except Exception as e:
        logger.error(f"❌ Erro ao fazer pergunta: {e}")

    # 5. Gerar áudio
    logger.info("🎙️  Gerando áudio...")
    try:
        audio = client.create_audio(
            notebook_id,
            format="standard",
            confirm=True
        )
        logger.info(f"✅ Áudio iniciado: {audio.get('id')}")
    except Exception as e:
        logger.warning(f"⚠️  Erro ao gerar áudio: {e}")

    # 6. Compartilhar
    logger.info("🔗 Compartilhando...")
    try:
        share = client.share_public(notebook_id)
        logger.info(f"✅ Link público: {share.get('url')}")
    except Exception as e:
        logger.warning(f"⚠️  Erro ao compartilhar: {e}")

    # 7. Listar todos os notebooks
    logger.info("📋 Listando notebooks...")
    try:
        notebooks = client.list_notebooks()
        logger.info(f"✅ Total: {len(notebooks)} notebooks")
        for nb in notebooks[:3]:
            logger.info(f"   - {nb.get('name')}")
    except Exception as e:
        logger.warning(f"⚠️  Erro ao listar: {e}")

    logger.info("\n✅ Exemplo concluído!")
    logger.info(f"\nPróximos passos:")
    logger.info(f"  1. Visite: https://notebooklm.google.com/notebooks/{notebook_id}")
    logger.info(f"  2. Faça mais perguntas")
    logger.info(f"  3. Gere mais conteúdo")
    logger.info(f"  4. Compartilhe com colaboradores")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Exemplo simples de uso do NotebookLM"
    )
    parser.add_argument(
        "--profile", "-p",
        default="default",
        help="Perfil NotebookLM"
    )

    args = parser.parse_args()
    main(profile=args.profile)
