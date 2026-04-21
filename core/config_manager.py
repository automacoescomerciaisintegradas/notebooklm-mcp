import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

def get_config() -> Dict[str, Any]:
    """
    Carrega as configurações do sistema a partir do diretório config.
    Suporta busca por chaves aninhadas usando notação de ponto.
    """
    config_dir = Path(__file__).parent.parent / "config"
    merged_config = {}

    # Carregar todos os arquivos JSON no diretório config
    if config_dir.exists():
        for config_file in config_dir.glob("*.json"):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    merged_config.update(data)
            except Exception as e:
                logger.error(f"Erro ao carregar {config_file}: {e}")

    return ConfigDict(merged_config)

class ConfigDict(dict):
    """Uma subclasse de dict que permite acesso por notação de ponto."""
    
    def get(self, key: str, default: Any = None) -> Any:
        if "." not in key:
            return super().get(key, default)
        
        parts = key.split(".")
        val = self
        for part in parts:
            if isinstance(val, dict) and part in val:
                val = val[part]
            else:
                return default
        return val
