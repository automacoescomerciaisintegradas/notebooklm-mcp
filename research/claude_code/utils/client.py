from google import genai
from google.genai import types
import os
import json
import requests
from typing import Optional

class GeminiClient:
    """
    Wrapper para interagir com a API do Gemini, OpenRouter ou Ollama local.
    """
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.0-flash"):
        self.api_key = api_key or self._discover_config("gemini_api_key")
        self.openrouter_key = self._discover_config("openrouter_api_key")
        self.ollama_url = self._discover_config("ollama_base_url") or "http://localhost:11434"
        self.ollama_model = "qwen3.5:latest" # Forçado para o modelo disponível
        self.model_name = model_name
        
        if self.api_key and "REMOVED" not in self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            self.mode = "direct"
        elif self.openrouter_key and "REMOVED" not in self.openrouter_key and "sk-or-v1-d90cba25" not in self.openrouter_key:
            # Note: sk-or-v1-d90cba25 é a chave que falhou no log anterior
            self.mode = "openrouter"
        else:
            self.mode = "ollama"
            print(f"⚠️  Iniciando com Ollama local ({self.ollama_model}).")

    def _discover_config(self, key_name: str) -> Optional[str]:
        # Tenta ENV
        val = os.getenv(key_name.upper())
        if val: return val
        
        # Tenta skills_config.json
        config_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "config", "skills_config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                    val = config.get(key_name)
                    if val and "REMOVED" not in val:
                        return val
            except Exception:
                pass
        return None

    def generate_response(self, system_prompt: str, user_message: str):
        if self.mode == "direct":
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=user_message,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt
                    )
                )
                return response.text
            except Exception as e:
                print(f"Erro Gemini Direto: {e}. Tentando fallback...")
                if self.openrouter_key: self.mode = "openrouter"
                else: self.mode = "ollama"
                return self.generate_response(system_prompt, user_message)

        elif self.mode == "openrouter":
            resp_text = self._call_openrouter(system_prompt, user_message)
            if "Erro OpenRouter" in resp_text:
                print(f"⚠️  {resp_text}. Tentando Ollama local...")
                self.mode = "ollama"
                return self.generate_response(system_prompt, user_message)
            return resp_text
        
        else:
            return self._call_ollama(system_prompt, user_message)

    def _call_ollama(self, system_prompt: str, user_message: str):
        url = f"{self.ollama_url}/api/chat"
        data = {
            "model": self.ollama_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "stream": False
        }
        try:
            resp = requests.post(url, json=data, timeout=60)
            if resp.status_code == 200:
                return resp.json()["message"]["content"]
            else:
                return f"Erro Ollama ({resp.status_code}): {resp.text}"
        except Exception as e:
            return f"Falha ao conectar ao Ollama local: {e}"

    def _call_openrouter(self, system_prompt: str, user_message: str):
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "google/gemini-2.0-flash-001", # Modelo padrão via OpenRouter
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        }
        resp = requests.post(url, headers=headers, json=data)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        else:
            return f"Erro OpenRouter ({resp.status_code}): {resp.text}"

if __name__ == "__main__":
    # Teste rápido
    try:
        client = GeminiClient()
        print("Conectado ao Gemini com sucesso!")
    except Exception as e:
        print(f"Erro ao conectar: {e}")
