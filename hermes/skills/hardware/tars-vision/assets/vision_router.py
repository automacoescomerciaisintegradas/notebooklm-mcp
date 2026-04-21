import threading
import time
import os
from huskylens_uart import HuskyLensDriver
from gesture_classifier import classify_gesture
import ha_controller

# Mapeamento de entidades do Home Assistant para gestos
GESTURE_ACTIONS = {
    "palm": "switch.fan_socket_1",
    "fist": "light.room_led_socket_1",
    "victory": "astronomy_news" # Aciona ação no Hermes em vez de HA
}

_current_gesture = None
_last_triggered_gesture = None
_stop_event = threading.Event()
_ha_warning_shown = False

def _trigger_ha_action(gesture):
    global _ha_warning_shown
    entity_id = GESTURE_ACTIONS.get(gesture)
    if not entity_id or entity_id == "astronomy_news":
        return

    try:
        domain = entity_id.split('.')[0]
        # Alternar estado (simplificado: ligar se detectar o gesto)
        ha_controller.call_service(domain, "turn_on", entity_id=entity_id)
        print(f"[vision_router] HA: {gesture.upper()} detectado -> Ligando {entity_id}")
    except RuntimeError as e:
        if not _ha_warning_shown:
            print(f"[vision_router] Home Assistant não configurado: {e}")
            _ha_warning_shown = True
    except Exception as e:
        print(f"[vision_router] Falha ao acionar HA para {gesture}: {e}")

def _capture_loop():
    # Inicializa o novo driver (tenta I2C, cai para simulação se falhar)
    huskylens = HuskyLensDriver()
    global _last_triggered_gesture
    
    print("[vision_router] Loop de captura iniciado.")
    
    while not _stop_event.is_set():
        try:
            # Obtém os 21 pontos (reais ou simulados)
            data = huskylens.get_landmarks()
            
            if data:
                gesture = classify_gesture(data)
                
                global _current_gesture
                _current_gesture = gesture

                # Lógica de trigger (apenas se o gesto mudar)
                if gesture and gesture != "unknown" and gesture != _last_triggered_gesture:
                    print(f"[vision_router] Gesto detectado: {gesture.upper()}")
                    
                    if gesture in ["palm", "fist"]:
                        _trigger_ha_action(gesture)
                    elif gesture == "victory":
                        print("[vision_router] VICTORY detectado! Solicitando notícias de astronomia...")
                        # Aqui poderia disparar um evento MQTT ou sinalizar ao Hermes Core
                    
                    _last_triggered_gesture = gesture
                elif gesture == "unknown":
                    _last_triggered_gesture = None
            else:
                _current_gesture = None
                _last_triggered_gesture = None

        except Exception as e:
            # print(f"[vision_router] Erro no loop de visão: {e}")
            pass
        time.sleep(0.1)

def start_capture():
    thread = threading.Thread(target=_capture_loop, daemon=True)
    thread.start()
    return thread

def stop_capture():
    _stop_event.set()

def get_current_gesture():
    return _current_gesture
