#!/usr/bin/env python3
"""
batch_operations.py — Operações em Lote

Exemplos de operações em batch com NotebookLM:
- Criar múltiplos notebooks
- Fazer múltiplas queries
- Gerar múltiplos áudios
- Baixar em paralelo

Uso:
    python batch_operations.py --action create --names "Proj1" "Proj2" "Proj3"
    python batch_operations.py --action query --notebook nb-123 --questions "P1" "P2" "P3"
    python batch_operations.py --action audio --notebooks nb-1 nb-2 nb-3
"""

import subprocess
import json
import sys
import argparse
from typing import List, Dict
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_nlm_cmd(cmd: List[str]) -> Dict:
    """Executar comando nlm e retornar resultado"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            check=True
        )
        return {
            "status": "success",
            "output": result.stdout.strip(),
            "command": " ".join(cmd)
        }
    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "error": e.stderr,
            "command": " ".join(cmd)
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "command": " ".join(cmd)
        }


def batch_create_notebooks(names: List[str], profile: str = "default") -> List[Dict]:
    """Criar múltiplos notebooks em paralelo"""
    logger.info(f"Criando {len(names)} notebooks...")

    def create_one(name):
        logger.info(f"  Criando: {name}")
        result = run_nlm_cmd(
            ["nlm", "notebook", "create", name, "--profile", profile, "--json"]
        )
        if result["status"] == "success":
            data = json.loads(result["output"])
            logger.info(f"    ✅ {data.get('id')}")
            return data
        else:
            logger.error(f"    ❌ Erro: {result.get('error')}")
            return None

    results = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(create_one, name) for name in names]
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    logger.info(f"✅ {len(results)}/{len(names)} notebooks criados")
    return results


def batch_query_notebook(
    notebook_id: str,
    questions: List[str],
    profile: str = "default"
) -> List[Dict]:
    """Fazer múltiplas queries ao mesmo notebook"""
    logger.info(f"Fazendo {len(questions)} queries ao notebook {notebook_id}...")

    def query_one(question):
        logger.info(f"  Q: {question[:50]}...")
        result = run_nlm_cmd(
            ["nlm", "notebook", "query", notebook_id, question, "--profile", profile]
        )
        return {
            "question": question,
            "answer": result["output"] if result["status"] == "success" else None,
            "status": result["status"]
        }

    results = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(query_one, q) for q in questions]
        for future in as_completed(futures):
            results.append(future.result())

    logger.info(f"✅ {len([r for r in results if r['status'] == 'success'])}/{len(questions)} queries concluídas")
    return results


def batch_create_audio(
    notebook_ids: List[str],
    profile: str = "default"
) -> List[Dict]:
    """Gerar áudio para múltiplos notebooks em paralelo"""
    logger.info(f"Gerando áudio para {len(notebook_ids)} notebooks...")

    def create_audio_one(nb_id):
        logger.info(f"  Gerando áudio: {nb_id}")
        result = run_nlm_cmd(
            ["nlm", "audio", "create", nb_id, "--confirm", "--profile", profile, "--json"]
        )
        if result["status"] == "success":
            data = json.loads(result["output"])
            logger.info(f"    ✅ {data.get('id')}")
            return data
        else:
            logger.error(f"    ❌ Erro")
            return None

    results = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(create_audio_one, nb_id) for nb_id in notebook_ids]
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    logger.info(f"✅ {len(results)}/{len(notebook_ids)} áudios iniciados")
    return results


def export_results(results: List[Dict], output_file: str = None):
    """Exportar resultados"""
    output = json.dumps(results, indent=2, ensure_ascii=False)

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output)
        logger.info(f"✅ Salvo: {output_file}")
    else:
        print(output)


def main():
    parser = argparse.ArgumentParser(description="Operações em Lote")
    parser.add_argument(
        "--action", "-a",
        choices=["create", "query", "audio"],
        required=True,
        help="Ação a executar"
    )
    parser.add_argument(
        "--names", "-n",
        nargs="+",
        help="Nomes de notebooks (para create)"
    )
    parser.add_argument(
        "--notebook", "-b",
        help="ID do notebook (para query)"
    )
    parser.add_argument(
        "--questions", "-q",
        nargs="+",
        help="Perguntas (para query)"
    )
    parser.add_argument(
        "--notebooks",
        nargs="+",
        help="IDs de notebooks (para audio)"
    )
    parser.add_argument(
        "--profile", "-p",
        default="default",
        help="Perfil NotebookLM"
    )
    parser.add_argument(
        "--output", "-o",
        help="Arquivo JSON de saída"
    )

    args = parser.parse_args()

    try:
        if args.action == "create":
            if not args.names:
                logger.error("--names é obrigatório para create")
                return 1
            results = batch_create_notebooks(args.names, args.profile)
            export_results(results, args.output)

        elif args.action == "query":
            if not args.notebook or not args.questions:
                logger.error("--notebook e --questions são obrigatórios para query")
                return 1
            results = batch_query_notebook(args.notebook, args.questions, args.profile)
            export_results(results, args.output)

        elif args.action == "audio":
            if not args.notebooks:
                logger.error("--notebooks é obrigatório para audio")
                return 1
            results = batch_create_audio(args.notebooks, args.profile)
            export_results(results, args.output)

        return 0

    except KeyboardInterrupt:
        logger.info("Cancelado")
        return 1
    except Exception as e:
        logger.error(f"Erro: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
