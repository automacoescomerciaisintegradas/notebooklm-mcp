# assets/ha_controller.py
"""Home Assistant Controller

Este módulo fornece uma camada REST simples para interagir com o Home Assistant
opcionalmente configurado. Utiliza a API HTTP do Home Assistant para enviar
comandos de controle de dispositivos (por exemplo, ligar/desligar ventilador
ou LED). Se as variáveis de ambiente ``HOME_ASSISTANT_URL`` e
``HOME_ASSISTANT_TOKEN`` não estiverem definidas, as funções retornam
``None`` ou levantam ``RuntimeError``.
"""

import os
import requests
from typing import Optional

# Configurações de ambiente
HA_URL = os.getenv("HOME_ASSISTANT_URL")
HA_TOKEN = os.getenv("HOME_ASSISTANT_TOKEN")

def _headers() -> dict:
    if not HA_TOKEN:
        raise RuntimeError("HOME_ASSISTANT_TOKEN não definido.")
    return {"Authorization": f"Bearer {HA_TOKEN}", "Content-Type": "application/json"}

def call_service(domain: str, service: str, entity_id: Optional[str] = None, data: Optional[dict] = None) -> dict:
    """Chama um serviço do Home Assistant.

    Args:
        domain: domínio do serviço (ex.: ``switch``).
        service: nome do serviço (ex.: ``turn_on``).
        entity_id: opcional, entidade alvo.
        data: payload adicional.
    Returns:
        Resposta JSON da API.
    """
    if not HA_URL:
        raise RuntimeError("HOME_ASSISTANT_URL não definido.")
    url = f"{HA_URL}/api/services/{domain}/{service}"
    payload = data or {}
    if entity_id:
        payload["entity_id"] = entity_id
    resp = requests.post(url, headers=_headers(), json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()

# Convenções de controle específicas para o TARS Vision
def toggle_fan(state: str = "on") -> dict:
    """Liga ou desliga o ventilador conectado ao Home Assistant.

    ``state`` pode ser ``"on"`` ou ``"off"``.
    """
    return call_service("switch", f"turn_{state}", entity_id="switch.tars_fan")

def toggle_room_led(state: str = "on") -> dict:
    """Liga ou desliga o LED da sala.
    """
    return call_service("light", f"turn_{state}", entity_id="light.tars_room_led")

if __name__ == "__main__":
    # Teste rápido ao executar o módulo
    try:
        print("Teste fan on:", toggle_fan("on"))
    except Exception as e:
        print("Erro ao chamar Home Assistant:", e)
