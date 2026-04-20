"""
Skills Extractor — AI Extractor
Processa transcripts de video via IA para extrair skills estruturadas.
Suporta: OpenAI, Google Gemini, Anthropic Claude, OpenRouter.

(c) Automacoes Comerciais Integradas 2026
"""

import json
import os
import re
from pathlib import Path
from typing import Optional
from datetime import datetime


EXTRACTION_PROMPT = """Voce e um especialista em extrair conhecimento pratico de conteudo educacional.

Analise o transcript abaixo e extraia SKILLS (habilidades praticas) que podem ser ensinadas a um agente de IA.

## Regras:
1. Cada skill deve ter: nome, descricao, passos praticos, e exemplos de uso
2. Foque em acoes concretas, nao teoria abstrata
3. Extraia de 3 a 10 skills por video
4. Cada skill deve ser auto-contida (usavel sem o video)
5. Inclua comandos, codigos ou templates quando mencionados
6. Responda em JSON valido

## Formato de saida (JSON):
{
  "video_title": "titulo do video",
  "video_summary": "resumo de 2-3 frases",
  "skills": [
    {
      "name": "Nome da Skill",
      "slug": "nome-da-skill",
      "description": "O que essa skill faz em 1-2 frases",
      "category": "categoria (ex: automacao, programacao, marketing, ia, devops)",
      "difficulty": "beginner|intermediate|advanced",
      "steps": [
        "Passo 1: ...",
        "Passo 2: ...",
        "Passo 3: ..."
      ],
      "examples": [
        "Exemplo pratico de uso"
      ],
      "tools_mentioned": ["ferramenta1", "ferramenta2"],
      "code_snippets": [
        {
          "language": "python",
          "code": "print('hello')",
          "description": "Exemplo basico"
        }
      ],
      "tags": ["tag1", "tag2"]
    }
  ],
  "total_skills": 5,
  "main_topics": ["topico1", "topico2"]
}

## Transcript:
{transcript}
"""


class AIExtractor:
    """Extrai skills estruturadas de transcripts usando IA."""

    def __init__(self, config_path: Path = None):
        self.config_path = config_path or Path(__file__).parent.parent / "config" / "skills_config.json"
        self.config = self._load_config()

    def _load_config(self) -> dict:
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_config(self, config: dict):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def extract_skills(self, transcript: str, video_title: str = "", provider: str = None) -> dict:
        """
        Extrai skills de um transcript usando IA.
        provider: 'openai', 'gemini', 'anthropic', ou auto-detect
        """
        if not transcript or len(transcript.strip()) < 100:
            return {"error": "Transcript muito curto para extrar skills"}

        # Truncar transcript muito longo (limite ~12k tokens)
        max_chars = 40000
        if len(transcript) > max_chars:
            transcript = transcript[:max_chars] + "\n\n[...transcript truncado...]"

        prompt = EXTRACTION_PROMPT.replace("{transcript}", transcript)

        # Auto-detect provider
        if not provider:
            provider = self._detect_provider()

        if not provider:
            return {"error": "Nenhuma API key configurada. Configure OPENAI_API_KEY, GEMINI_API_KEY ou ANTHROPIC_API_KEY"}

        extractors = {
            "openai": self._extract_openai,
            "gemini": self._extract_gemini,
            "anthropic": self._extract_anthropic,
            "openrouter": self._extract_openrouter,
        }

        extractor = extractors.get(provider)
        if not extractor:
            return {"error": f"Provider desconhecido: {provider}"}

        result = extractor(prompt)

        # Fallback: se o provider principal falhou, tentar os outros
        if "error" in result:
            fallback_order = [p for p in ["gemini", "openai", "anthropic", "openrouter"] if p != provider]
            for fallback in fallback_order:
                if self._has_api_key(fallback):
                    fb_result = extractors[fallback](prompt)
                    if "error" not in fb_result:
                        fb_result["fallback_from"] = provider
                        result = fb_result
                        provider = fallback
                        break

        if "error" not in result:
            result["provider"] = provider
            result["extracted_at"] = datetime.now().isoformat()
            if video_title:
                result["video_title"] = video_title

        return result

    def _detect_provider(self) -> Optional[str]:
        """Detecta qual provider de IA esta disponivel."""
        # Checar config
        provider = self.config.get("ai_provider")
        if provider:
            return provider

        # Checar env vars
        if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
            return "gemini"
        if os.environ.get("OPENAI_API_KEY"):
            return "openai"
        if os.environ.get("ANTHROPIC_API_KEY"):
            return "anthropic"
        if os.environ.get("OPENROUTER_API_KEY"):
            return "openrouter"

        return None

    def _has_api_key(self, provider: str) -> bool:
        """Verifica se existe API key para o provider."""
        if provider == "gemini":
            return bool(self.config.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
        if provider == "openai":
            return bool(self.config.get("openai_api_key") or os.environ.get("OPENAI_API_KEY"))
        if provider == "anthropic":
            return bool(self.config.get("anthropic_api_key") or os.environ.get("ANTHROPIC_API_KEY"))
        if provider == "openrouter":
            return bool(self.config.get("openrouter_api_key") or os.environ.get("OPENROUTER_API_KEY"))
        return False

    def _extract_openai(self, prompt: str) -> dict:
        """Extrai via OpenAI API."""
        try:
            from openai import OpenAI

            api_key = self.config.get("openai_api_key") or os.environ.get("OPENAI_API_KEY")
            if not api_key:
                return {"error": "OPENAI_API_KEY nao configurada"}

            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=self.config.get("openai_model", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": "Voce extrai skills praticas de videos. Sempre responda em JSON valido."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            return self._parse_json_response(content)

        except ImportError:
            return {"error": "openai nao instalado: pip install openai"}
        except Exception as e:
            return {"error": f"OpenAI: {str(e)}"}

    def _extract_gemini(self, prompt: str) -> dict:
        """Extrai via Google Gemini API."""
        try:
            import google.generativeai as genai

            api_key = (
                self.config.get("gemini_api_key")
                or os.environ.get("GEMINI_API_KEY")
                or os.environ.get("GOOGLE_API_KEY")
            )
            if not api_key:
                return {"error": "GEMINI_API_KEY nao configurada"}

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                self.config.get("gemini_model", "gemini-2.0-flash"),
                generation_config={"temperature": 0.3, "response_mime_type": "application/json"},
            )

            response = model.generate_content(prompt)
            return self._parse_json_response(response.text)

        except ImportError:
            return {"error": "google-generativeai nao instalado: pip install google-generativeai"}
        except Exception as e:
            return {"error": f"Gemini: {str(e)}"}

    def _extract_anthropic(self, prompt: str) -> dict:
        """Extrai via Anthropic Claude API."""
        try:
            from anthropic import Anthropic

            api_key = self.config.get("anthropic_api_key") or os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                return {"error": "ANTHROPIC_API_KEY nao configurada"}

            client = Anthropic(api_key=api_key)
            response = client.messages.create(
                model=self.config.get("anthropic_model", "claude-sonnet-4-20250514"),
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt},
                ],
            )

            content = response.content[0].text
            return self._parse_json_response(content)

        except ImportError:
            return {"error": "anthropic nao instalado: pip install anthropic"}
        except Exception as e:
            return {"error": f"Anthropic: {str(e)}"}

    def _extract_openrouter(self, prompt: str) -> dict:
        """Extrai via OpenRouter (API compativel com OpenAI)."""
        try:
            from openai import OpenAI

            api_key = self.config.get("openrouter_api_key") or os.environ.get("OPENROUTER_API_KEY")
            if not api_key:
                return {"error": "OPENROUTER_API_KEY nao configurada"}

            client = OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
            )
            model = self.config.get("openrouter_model", "google/gemini-2.0-flash-exp:free")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Voce extrai skills praticas de videos. Sempre responda em JSON valido."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=4096,
            )

            content = response.choices[0].message.content
            return self._parse_json_response(content)

        except ImportError:
            return {"error": "openai nao instalado: pip install openai"}
        except Exception as e:
            return {"error": f"OpenRouter: {str(e)}"}

    def _parse_json_response(self, text: str) -> dict:
        """Parse JSON da resposta da IA, extraindo de markdown code blocks se necessario."""
        text = text.strip()

        # Remover code blocks markdown
        match = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', text, re.DOTALL)
        if match:
            text = match.group(1).strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            return {"error": f"JSON invalido da IA: {str(e)}", "raw_response": text[:500]}

    def set_api_key(self, provider: str, api_key: str, model: str = None):
        """Salva API key e modelo na config."""
        key_map = {
            "openai": "openai_api_key",
            "gemini": "gemini_api_key",
            "anthropic": "anthropic_api_key",
            "openrouter": "openrouter_api_key",
        }
        model_map = {
            "openai": "openai_model",
            "gemini": "gemini_model",
            "anthropic": "anthropic_model",
            "openrouter": "openrouter_model",
        }
        if provider in key_map:
            self.config[key_map[provider]] = api_key
            self.config["ai_provider"] = provider
            if model and provider in model_map:
                self.config[model_map[provider]] = model
            self._save_config(self.config)

    def get_status(self) -> dict:
        """Retorna status das APIs configuradas."""
        return {
            "configured_provider": self.config.get("ai_provider"),
            "openai": bool(self.config.get("openai_api_key") or os.environ.get("OPENAI_API_KEY")),
            "gemini": bool(self.config.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")),
            "anthropic": bool(self.config.get("anthropic_api_key") or os.environ.get("ANTHROPIC_API_KEY")),
            "openrouter": bool(self.config.get("openrouter_api_key") or os.environ.get("OPENROUTER_API_KEY")),
        }
