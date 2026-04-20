#!/usr/bin/env python3
"""
cross_notebook_analysis.py — Análise Cross-Notebook

Faz a mesma pergunta a múltiplos notebooks e:
1. Coleta respostas
2. Compara achados
3. Consolida em resumo

Uso:
    python cross_notebook_analysis.py "notebook1" "notebook2" "notebook3" \
        --question "Quais são os principais desafios?" \
        --profile work
"""

import subprocess
import json
import sys
import argparse
from typing import List, Dict
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def query_notebook(
    notebook_id: str,
    question: str,
    profile: str = "default"
) -> Dict:
    """Query um notebook e retornar resposta"""
    cmd = [
        "nlm", "notebook", "query",
        notebook_id, question,
        "--profile", profile,
        "--json"
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            check=True
        )
        data = json.loads(result.stdout)
        return {
            "notebook_id": notebook_id,
            "question": question,
            "answer": data.get("answer", ""),
            "sources": data.get("sources", []),
            "status": "success"
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao queryar {notebook_id}: {e.stderr}")
        return {
            "notebook_id": notebook_id,
            "question": question,
            "status": "error",
            "error": e.stderr
        }
    except json.JSONDecodeError:
        logger.error(f"Erro ao parsear resposta de {notebook_id}")
        return {
            "notebook_id": notebook_id,
            "question": question,
            "status": "parse_error"
        }


def analyze_notebooks(
    notebook_ids: List[str],
    question: str,
    profile: str = "default"
) -> Dict:
    """Análise cross-notebook"""

    logger.info(f"Analisando {len(notebook_ids)} notebooks...")
    logger.info(f"Pergunta: {question}")
    logger.info("")

    results = []

    for i, nb_id in enumerate(notebook_ids, 1):
        logger.info(f"[{i}/{len(notebook_ids)}] Consultando {nb_id}...")
        result = query_notebook(nb_id, question, profile)

        if result["status"] == "success":
            logger.info(f"  ✅ Resposta recebida ({len(result['answer'])} caracteres)")
            results.append(result)
        else:
            logger.warning(f"  ⚠️  Erro: {result.get('error', 'desconhecido')}")

    logger.info("")

    # Análise
    logger.info("📊 Análise:")
    logger.info(f"  - Total: {len(notebook_ids)} notebooks")
    logger.info(f"  - Sucesso: {len([r for r in results if r['status'] == 'success'])}")
    logger.info(f"  - Falhas: {len([r for r in results if r['status'] != 'success'])}")
    logger.info("")

    return {
        "question": question,
        "notebooks_analyzed": len(notebook_ids),
        "results": results,
        "timestamp": __import__("datetime").datetime.now().isoformat()
    }


def export_results(analysis: Dict, output_file: str = None):
    """Exportar resultados em JSON e Markdown"""

    # JSON
    json_output = json.dumps(analysis, indent=2, ensure_ascii=False)
    if output_file:
        json_path = output_file.replace(".md", ".json")
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(json_output)
        logger.info(f"✅ Salvo: {json_path}")

    # Markdown
    md_lines = [
        "# Cross-Notebook Analysis",
        "",
        f"**Question:** {analysis['question']}",
        "",
        f"**Notebooks:** {analysis['notebooks_analyzed']}",
        f"**Timestamp:** {analysis['timestamp']}",
        "",
        "---",
        ""
    ]

    for result in analysis['results']:
        md_lines.extend([
            f"## {result['notebook_id']}",
            "",
            "**Status:** ✅" if result['status'] == 'success' else "**Status:** ❌",
            "",
        ])

        if result['status'] == 'success':
            md_lines.extend([
                "**Answer:**",
                "",
                f"> {result['answer'][:500]}...",  # Primeiros 500 chars
                "",
            ])

            if result['sources']:
                md_lines.extend([
                    "**Sources:**",
                    "",
                ])
                for source in result['sources'][:3]:
                    md_lines.append(f"- {source}")
                md_lines.append("")

        md_lines.append("---")
        md_lines.append("")

    md_output = "\n".join(md_lines)

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(md_output)
        logger.info(f"✅ Salvo: {output_file}")
    else:
        print(md_output)


def main():
    parser = argparse.ArgumentParser(
        description="Análise Cross-Notebook"
    )
    parser.add_argument(
        "notebooks",
        nargs="+",
        help="IDs dos notebooks a analisar"
    )
    parser.add_argument(
        "--question", "-q",
        required=True,
        help="Pergunta a fazer"
    )
    parser.add_argument(
        "--profile", "-p",
        default="default",
        help="Perfil NotebookLM"
    )
    parser.add_argument(
        "--output", "-o",
        help="Arquivo de saída (JSON + Markdown)"
    )

    args = parser.parse_args()

    try:
        analysis = analyze_notebooks(
            args.notebooks,
            args.question,
            args.profile
        )

        if args.output:
            export_results(analysis, args.output)
        else:
            export_results(analysis)

        return 0

    except KeyboardInterrupt:
        logger.info("Cancelado pelo usuário")
        return 1
    except Exception as e:
        logger.error(f"Erro: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
