"""
Skills Extractor — Video Processor
Extrai transcripts de videos do YouTube usando youtube-transcript-api e yt-dlp.

(c) Automacoes Comerciais Integradas 2026
"""

import re
import json
from pathlib import Path
from typing import Optional
from datetime import datetime


class VideoProcessor:
    """Extrai transcript e metadata de videos do YouTube."""

    YOUTUBE_REGEX = re.compile(
        r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)([\w-]{11})'
    )

    def __init__(self, cache_dir: Path = None):
        self.cache_dir = cache_dir or Path(__file__).parent.parent / "skills" / ".cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def extract_video_id(self, url: str) -> Optional[str]:
        """Extrai o video ID de uma URL do YouTube."""
        match = self.YOUTUBE_REGEX.search(url)
        return match.group(1) if match else None

    def get_transcript(self, url: str, languages: list = None) -> dict:
        """
        Extrai transcript de um video do YouTube.
        Retorna: {video_id, title, transcript, language, duration_seconds, source}
        """
        video_id = self.extract_video_id(url)
        if not video_id:
            return {"error": f"URL invalida: {url}"}

        # Checar cache
        cached = self._load_cache(video_id)
        if cached:
            cached["from_cache"] = True
            return cached

        languages = languages or ["pt", "pt-BR", "en", "es", "auto"]

        # Tentar youtube-transcript-api primeiro
        result = self._try_transcript_api(video_id, languages)

        # Fallback: yt-dlp
        if "error" in result:
            result = self._try_ytdlp(video_id, url, languages)

        if "error" not in result:
            self._save_cache(video_id, result)

        return result

    def _try_transcript_api(self, video_id: str, languages: list) -> dict:
        """Tenta extrair transcript via youtube-transcript-api."""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi

            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            # Tentar transcript manual primeiro, depois gerado automaticamente
            transcript = None
            lang = None

            for lang_code in languages:
                try:
                    transcript = transcript_list.find_transcript([lang_code])
                    lang = lang_code
                    break
                except Exception:
                    continue

            if not transcript:
                # Pegar qualquer um disponivel
                for t in transcript_list:
                    transcript = t
                    lang = t.language_code
                    break

            if not transcript:
                return {"error": "Nenhum transcript encontrado"}

            data = transcript.fetch()
            full_text = " ".join([entry["text"] for entry in data])
            duration = max(entry["start"] + entry.get("duration", 0) for entry in data) if data else 0

            return {
                "video_id": video_id,
                "title": self._get_title(video_id),
                "transcript": full_text,
                "segments": data,
                "language": lang,
                "duration_seconds": int(duration),
                "source": "youtube-transcript-api",
                "extracted_at": datetime.now().isoformat(),
            }

        except ImportError:
            return {"error": "youtube-transcript-api nao instalado"}
        except Exception as e:
            return {"error": f"transcript-api: {str(e)}"}

    def _try_ytdlp(self, video_id: str, url: str, languages: list) -> dict:
        """Fallback: extrai transcript via yt-dlp."""
        try:
            import subprocess
            import tempfile

            with tempfile.TemporaryDirectory() as tmpdir:
                lang_str = ",".join(languages[:3])
                cmd = [
                    "yt-dlp",
                    "--skip-download",
                    "--write-auto-sub",
                    "--write-sub",
                    f"--sub-lang={lang_str}",
                    "--sub-format=json3",
                    "--print=%(title)s",
                    "-o", f"{tmpdir}/%(id)s",
                    url,
                ]

                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=60
                )

                title = result.stdout.strip().split("\n")[0] if result.stdout else video_id

                # Procurar arquivo de legenda gerado
                sub_files = list(Path(tmpdir).glob(f"{video_id}*.json3"))
                if not sub_files:
                    sub_files = list(Path(tmpdir).glob("*.json3"))

                if not sub_files:
                    return {"error": "yt-dlp: nenhuma legenda encontrada"}

                with open(sub_files[0], "r", encoding="utf-8") as f:
                    sub_data = json.load(f)

                events = sub_data.get("events", [])
                segments = []
                full_text_parts = []

                for event in events:
                    segs = event.get("segs", [])
                    text = "".join(s.get("utf8", "") for s in segs).strip()
                    if text and text != "\n":
                        start = event.get("tStartMs", 0) / 1000
                        dur = event.get("dDurationMs", 0) / 1000
                        segments.append({"start": start, "duration": dur, "text": text})
                        full_text_parts.append(text)

                duration = max(s["start"] + s["duration"] for s in segments) if segments else 0

                return {
                    "video_id": video_id,
                    "title": title,
                    "transcript": " ".join(full_text_parts),
                    "segments": segments,
                    "language": "auto",
                    "duration_seconds": int(duration),
                    "source": "yt-dlp",
                    "extracted_at": datetime.now().isoformat(),
                }

        except FileNotFoundError:
            return {"error": "yt-dlp nao instalado"}
        except Exception as e:
            return {"error": f"yt-dlp: {str(e)}"}

    def _get_title(self, video_id: str) -> str:
        """Tenta obter titulo do video."""
        try:
            import subprocess
            result = subprocess.run(
                ["yt-dlp", "--skip-download", "--print=%(title)s",
                 f"https://youtube.com/watch?v={video_id}"],
                capture_output=True, text=True, timeout=15,
            )
            return result.stdout.strip() or video_id
        except Exception:
            return video_id

    def _load_cache(self, video_id: str) -> Optional[dict]:
        cache_file = self.cache_dir / f"{video_id}.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return None

    def _save_cache(self, video_id: str, data: dict):
        cache_file = self.cache_dir / f"{video_id}.json"
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def process_urls(self, urls: list[str]) -> list[dict]:
        """Processa multiplas URLs e retorna lista de transcripts."""
        results = []
        for url in urls:
            url = url.strip()
            if url:
                result = self.get_transcript(url)
                result["url"] = url
                results.append(result)
        return results
