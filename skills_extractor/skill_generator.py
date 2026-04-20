"""
Skills Extractor — Skill Generator
Converte skills extraidas pela IA em arquivos MCP-compativeis:
- SKILL.md (documentacao)
- skill.py (implementacao Python com ferramentas MCP)
- metadata.json (metadados para indexacao)

(c) Automacoes Comerciais Integradas 2026
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Optional


class SkillGenerator:
    """Gera arquivos de skill MCP a partir de dados extraidos pela IA."""

    def __init__(self, skills_dir: Path = None):
        self.skills_dir = skills_dir or Path(__file__).parent.parent / "skills"
        self.skills_dir.mkdir(parents=True, exist_ok=True)

    def generate_skill(self, skill_data: dict, video_info: dict = None) -> dict:
        """
        Gera todos os arquivos de uma skill.
        Retorna: {name, slug, path, files: [SKILL.md, skill.py, metadata.json]}
        """
        name = skill_data.get("name", "Unnamed Skill")
        slug = skill_data.get("slug") or self._slugify(name)

        skill_dir = self.skills_dir / slug
        skill_dir.mkdir(parents=True, exist_ok=True)

        # Gerar arquivos
        md_path = self._generate_skill_md(skill_dir, skill_data, video_info)
        py_path = self._generate_skill_py(skill_dir, skill_data)
        meta_path = self._generate_metadata(skill_dir, skill_data, video_info)

        return {
            "name": name,
            "slug": slug,
            "path": str(skill_dir),
            "files": [str(md_path), str(py_path), str(meta_path)],
        }

    def generate_all_skills(self, extraction_result: dict, video_info: dict = None) -> list[dict]:
        """Gera todas as skills de um resultado de extracao."""
        skills = extraction_result.get("skills", [])
        results = []

        for skill_data in skills:
            result = self.generate_skill(skill_data, video_info)
            results.append(result)

        return results

    def _generate_skill_md(self, skill_dir: Path, skill: dict, video_info: dict = None) -> Path:
        """Gera SKILL.md com documentacao completa."""
        name = skill.get("name", "Skill")
        desc = skill.get("description", "")
        steps = skill.get("steps", [])
        examples = skill.get("examples", [])
        tools = skill.get("tools_mentioned", [])
        snippets = skill.get("code_snippets", [])
        tags = skill.get("tags", [])
        category = skill.get("category", "geral")
        difficulty = skill.get("difficulty", "intermediate")

        lines = [
            f"# {name}",
            "",
            f"> {desc}",
            "",
            f"**Categoria:** {category}  ",
            f"**Dificuldade:** {difficulty}  ",
            f"**Tags:** {', '.join(tags)}",
            "",
        ]

        if video_info:
            title = video_info.get("title", "")
            vid = video_info.get("video_id", "")
            if title:
                lines.extend([
                    f"**Fonte:** [{title}](https://youtube.com/watch?v={vid})",
                    "",
                ])

        lines.extend(["---", "", "## Passos", ""])
        for i, step in enumerate(steps, 1):
            lines.append(f"{i}. {step}")
        lines.append("")

        if examples:
            lines.extend(["## Exemplos de Uso", ""])
            for ex in examples:
                lines.append(f"- {ex}")
            lines.append("")

        if snippets:
            lines.extend(["## Codigo", ""])
            for snip in snippets:
                lang = snip.get("language", "")
                code = snip.get("code", "")
                snip_desc = snip.get("description", "")
                if snip_desc:
                    lines.append(f"### {snip_desc}")
                    lines.append("")
                lines.append(f"```{lang}")
                lines.append(code)
                lines.append("```")
                lines.append("")

        if tools:
            lines.extend(["## Ferramentas Mencionadas", ""])
            for t in tools:
                lines.append(f"- {t}")
            lines.append("")

        lines.extend([
            "---",
            "",
            f"*Extraido automaticamente por Skills Extractor — {datetime.now().strftime('%Y-%m-%d')}*",
            f"*(c) Automacoes Comerciais Integradas 2026*",
        ])

        path = skill_dir / "SKILL.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def _generate_skill_py(self, skill_dir: Path, skill: dict) -> Path:
        """Gera skill.py com ferramentas MCP."""
        name = skill.get("name", "Skill")
        slug = skill.get("slug") or self._slugify(name)
        desc = skill.get("description", "")
        steps = skill.get("steps", [])
        examples = skill.get("examples", [])
        snippets = skill.get("code_snippets", [])
        func_name = re.sub(r'[^a-z0-9_]', '_', slug.replace('-', '_'))

        steps_str = json.dumps(steps, ensure_ascii=False, indent=8)
        examples_str = json.dumps(examples, ensure_ascii=False, indent=8)

        # Coletar code snippets como ferramentas extras
        extra_tools = []
        for i, snip in enumerate(snippets):
            snip_desc = snip.get("description", f"Code snippet {i+1}")
            snip_code = snip.get("code", "")
            snip_lang = snip.get("language", "text")
            extra_tools.append({
                "desc": snip_desc,
                "code": snip_code,
                "lang": snip_lang,
            })

        code = f'''"""
MCP Skill: {name}
{desc}

Auto-gerado por Skills Extractor
(c) Automacoes Comerciais Integradas 2026
"""

import json
import sys


SKILL_NAME = "{name}"
SKILL_DESCRIPTION = """{desc}"""
SKILL_STEPS = {steps_str}
SKILL_EXAMPLES = {examples_str}


def get_skill_info() -> dict:
    """Retorna informacoes completas da skill."""
    return {{
        "name": SKILL_NAME,
        "description": SKILL_DESCRIPTION,
        "steps": SKILL_STEPS,
        "examples": SKILL_EXAMPLES,
    }}


def execute_skill(query: str = "") -> dict:
    """
    Executa a skill respondendo perguntas baseadas no conhecimento extraido.
    Args:
        query: Pergunta ou contexto para aplicar a skill
    Returns:
        Resposta com passos e exemplos relevantes
    """
    info = get_skill_info()

    if not query:
        return {{
            "skill": info["name"],
            "message": "Use esta skill fazendo uma pergunta relacionada.",
            "steps": info["steps"],
            "examples": info["examples"],
        }}

    return {{
        "skill": info["name"],
        "query": query,
        "guidance": info["description"],
        "steps": info["steps"],
        "examples": info["examples"],
        "tip": "Siga os passos acima para executar esta skill.",
    }}


# === MCP Tool Definitions ===

TOOLS = [
    {{
        "name": "{func_name}_info",
        "description": "Retorna informacoes da skill: {name}",
        "inputSchema": {{
            "type": "object",
            "properties": {{}},
        }},
    }},
    {{
        "name": "{func_name}_execute",
        "description": "{desc}",
        "inputSchema": {{
            "type": "object",
            "properties": {{
                "query": {{
                    "type": "string",
                    "description": "Pergunta ou contexto para aplicar a skill",
                }},
            }},
        }},
    }},
]


def handle_tool_call(tool_name: str, arguments: dict) -> str:
    """Handler para chamadas de ferramentas MCP."""
    if tool_name == "{func_name}_info":
        return json.dumps(get_skill_info(), ensure_ascii=False, indent=2)
    elif tool_name == "{func_name}_execute":
        result = execute_skill(arguments.get("query", ""))
        return json.dumps(result, ensure_ascii=False, indent=2)
    else:
        return json.dumps({{"error": f"Tool desconhecida: {{tool_name}}"}})


if __name__ == "__main__":
    # Teste rapido
    print(json.dumps(get_skill_info(), ensure_ascii=False, indent=2))
'''

        path = skill_dir / "skill.py"
        path.write_text(code, encoding="utf-8")
        return path

    def _generate_metadata(self, skill_dir: Path, skill: dict, video_info: dict = None) -> Path:
        """Gera metadata.json."""
        metadata = {
            "name": skill.get("name"),
            "slug": skill.get("slug") or self._slugify(skill.get("name", "")),
            "description": skill.get("description"),
            "category": skill.get("category", "geral"),
            "difficulty": skill.get("difficulty", "intermediate"),
            "tags": skill.get("tags", []),
            "tools_mentioned": skill.get("tools_mentioned", []),
            "created_at": datetime.now().isoformat(),
            "source": "skills_extractor",
            "version": "1.0.0",
        }

        if video_info:
            metadata["video"] = {
                "id": video_info.get("video_id"),
                "title": video_info.get("title"),
                "url": video_info.get("url"),
                "duration": video_info.get("duration_seconds"),
            }

        path = skill_dir / "metadata.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        return path

    def list_skills(self) -> list[dict]:
        """Lista todas as skills geradas."""
        skills = []
        for meta_file in self.skills_dir.glob("*/metadata.json"):
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                meta["path"] = str(meta_file.parent)
                skills.append(meta)
            except Exception:
                continue
        return skills

    def get_skill(self, slug: str) -> Optional[dict]:
        """Retorna dados completos de uma skill."""
        skill_dir = self.skills_dir / slug
        meta_file = skill_dir / "metadata.json"
        skill_md = skill_dir / "SKILL.md"

        if not meta_file.exists():
            return None

        with open(meta_file, "r", encoding="utf-8") as f:
            meta = json.load(f)

        if skill_md.exists():
            meta["documentation"] = skill_md.read_text(encoding="utf-8")

        meta["path"] = str(skill_dir)
        return meta

    def delete_skill(self, slug: str) -> bool:
        """Remove uma skill."""
        import shutil
        skill_dir = self.skills_dir / slug
        if skill_dir.exists():
            shutil.rmtree(skill_dir)
            return True
        return False

    def _slugify(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s_]+', '-', text)
        text = re.sub(r'-+', '-', text)
        return text.strip('-')[:60]
