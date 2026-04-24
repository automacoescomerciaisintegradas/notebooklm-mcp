"""
Skills Extractor — DOM Extractor (sem LLM)
Gera skills estruturadas a partir de metadados do YouTube
extraídos pela extensão Chrome (título, descrição, capítulos, tags).

Não consome tokens de LLM — lógica 100% determinística.

(c) Automacoes Comerciais Integradas 2026
"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Optional


# Mapeamento de categorias do YouTube → categorias de skill
CATEGORY_MAP = {
    "Education": "education",
    "Science & Technology": "technology",
    "Howto & Style": "how-to",
    "Gaming": "gaming",
    "News & Politics": "news",
    "Business": "business",
    "People & Blogs": "general",
    "Entertainment": "entertainment",
    "Film & Animation": "creative",
    "Music": "creative",
    "Sports": "sports",
    "Travel & Events": "general",
    "Autos & Vehicles": "general",
    "Pets & Animals": "general",
    "Comedy": "entertainment",
    "Nonprofits & Activism": "general",
}

# Heurística de dificuldade baseada na duração
DIFFICULTY_BY_DURATION = [
    (600,   "beginner"),      # < 10 min
    (1800,  "intermediate"),  # < 30 min
    (3600,  "advanced"),      # < 60 min
]


def _slugify(text: str) -> str:
    """Converte título para slug de arquivo."""
    slug = text.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = re.sub(r'^-+|-+$', '', slug)
    return slug[:60]


def _estimate_difficulty(duration_seconds: int) -> str:
    for threshold, label in DIFFICULTY_BY_DURATION:
        if duration_seconds < threshold:
            return label
    return "advanced"


def _extract_key_topics(title: str, description: str, tags: list, chapters: list) -> list:
    """
    Extrai tópicos principais sem LLM:
    1. Tags do YouTube (mais confiáveis)
    2. Capítulos (se houver, representam a estrutura real do conteúdo)
    3. Palavras-chave do título (excluindo stopwords)
    """
    topics = set()

    # Tags do YouTube
    for tag in (tags or [])[:8]:
        if len(tag) > 2:
            topics.add(tag.strip().lower())

    # Capítulos — são os melhores tópicos
    for chapter in (chapters or [])[:10]:
        # Remove timestamp da frente (ex: "0:00 - Introdução" → "Introdução")
        clean = re.sub(r'^\d+:\d+(?::\d+)?\s*[-–]\s*', '', chapter).strip()
        if len(clean) > 3:
            topics.add(clean)

    # Palavras do título (heurística simples)
    STOPWORDS = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
                 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                 'would', 'could', 'should', 'may', 'might', 'shall', 'can', 'de', 'da',
                 'do', 'em', 'no', 'na', 'com', 'por', 'para', 'que', 'e', 'o', 'a',
                 'os', 'as', 'um', 'uma', 'se', 'é', 'como', 'eu', 'você', 'seu', 'sua'}
    title_words = re.findall(r'\b\w{4,}\b', title.lower())
    for word in title_words:
        if word not in STOPWORDS:
            topics.add(word)

    return list(topics)[:12]


def _build_markdown_skill(metadata: dict, skill_name: str, topics: list,
                           difficulty: str, category: str) -> str:
    """Gera o arquivo SKILL.md sem LLM."""
    chapters_section = ""
    if metadata.get("chapters"):
        chapters_md = "\n".join(f"- {c}" for c in metadata["chapters"])
        chapters_section = f"""
## 📚 Capítulos

{chapters_md}
"""

    tags_section = ""
    if metadata.get("tags"):
        tags_md = " · ".join(f"`{t}`" for t in metadata["tags"][:10])
        tags_section = f"""
## 🏷️ Tags

{tags_md}
"""

    return f"""---
name: "{skill_name}"
description: "{metadata.get('description', '')[:200].replace(chr(10), ' ')}"
category: "{category}"
difficulty: "{difficulty}"
source_url: "{metadata.get('url', '')}"
video_id: "{metadata.get('video_id', '')}"
channel: "{metadata.get('channel', '')}"
duration: "{metadata.get('duration_str', '')}"
extracted_at: "{datetime.now().isoformat()}"
source: "chrome_extension_dom"
notebooklm_added: {str(metadata.get('notebooklm_added', False)).lower()}
tags: {json.dumps(topics[:8])}
---

# {skill_name}

**Canal:** {metadata.get('channel', 'N/A')}  
**Duração:** {metadata.get('duration_str', 'N/A')}  
**Fonte:** [{metadata.get('url', '')}]({metadata.get('url', '')})
{f"**NotebookLM:** ✅ Adicionado como fonte" if metadata.get('notebooklm_added') else ""}

## 📝 Descrição

{metadata.get('description', 'N/A')}
{chapters_section}{tags_section}
## 🎯 Tópicos Identificados

{chr(10).join(f"- {t}" for t in topics) if topics else "- N/A"}

## 💡 Uso

Esta skill foi extraída automaticamente da extensão Chrome NotebookLM V2.  
Para aprofundamento, acesse o vídeo ou consulte o notebook no NotebookLM.
"""


class DOMExtractor:
    """
    Gera skills estruturadas a partir de metadados extraídos pela extensão Chrome.
    Não usa LLM — processamento 100% determinístico.
    """

    def __init__(self, skills_dir: Path = None):
        self.skills_dir = skills_dir or Path(__file__).parent.parent / "skills"
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self._index_file = self.skills_dir / "_index.json"
        self._index = self._load_index()

    def _load_index(self) -> list:
        if self._index_file.exists():
            try:
                with open(self._index_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_index(self):
        with open(self._index_file, "w", encoding="utf-8") as f:
            json.dump(self._index, f, ensure_ascii=False, indent=2)

    def ingest(self, metadata: dict) -> dict:
        """
        Processa metadados da extensão e gera skill sem LLM.
        Retorna: {slug, skill_name, path, topics, difficulty, category, already_existed}
        """
        video_id = metadata.get("video_id", "")
        title = metadata.get("title", "Unknown Video")

        # Verificar se já existe
        existing = next((s for s in self._index if s.get("video_id") == video_id), None)
        if existing:
            return {**existing, "already_existed": True}

        # Processar metadados
        skill_name = title
        slug = _slugify(title) or video_id
        category = CATEGORY_MAP.get(metadata.get("category", ""), "general")
        difficulty = _estimate_difficulty(metadata.get("duration_seconds", 0))
        topics = _extract_key_topics(
            title,
            metadata.get("description", ""),
            metadata.get("tags", []),
            metadata.get("chapters", []),
        )

        # Criar diretório da skill
        skill_dir = self.skills_dir / slug
        skill_dir.mkdir(parents=True, exist_ok=True)

        # Gerar SKILL.md
        skill_md = _build_markdown_skill(metadata, skill_name, topics, difficulty, category)
        skill_file = skill_dir / "SKILL.md"
        with open(skill_file, "w", encoding="utf-8") as f:
            f.write(skill_md)

        # Salvar metadados raw
        meta_file = skill_dir / "metadata.json"
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        # Atualizar índice
        entry = {
            "slug": slug,
            "name": skill_name,
            "description": metadata.get("description", "")[:200],
            "category": category,
            "difficulty": difficulty,
            "tags": topics[:8],
            "video_id": video_id,
            "url": metadata.get("url", ""),
            "channel": metadata.get("channel", ""),
            "duration": metadata.get("duration_str", ""),
            "path": str(skill_file),
            "notebooklm_added": metadata.get("notebooklm_added", False),
            "created_at": datetime.now().isoformat(),
            "source": "chrome_extension_dom",
        }
        self._index.append(entry)
        self._save_index()

        return {**entry, "already_existed": False}

    def list_skills(self) -> list:
        return self._index

    def get_skill(self, slug: str) -> Optional[dict]:
        return next((s for s in self._index if s["slug"] == slug), None)

    def delete_skill(self, slug: str) -> bool:
        skill = self.get_skill(slug)
        if not skill:
            return False
        # Remove arquivos
        skill_dir = self.skills_dir / slug
        if skill_dir.exists():
            import shutil
            shutil.rmtree(skill_dir)
        self._index = [s for s in self._index if s["slug"] != slug]
        self._save_index()
        return True
