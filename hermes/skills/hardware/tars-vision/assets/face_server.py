# assets/face_server.py
"""Face Server

Este módulo expõe uma API Flask que gerencia o pipeline de voz (captura, transcrição via Whisper,
resposta TTS via OpenAI) e executa um "heartbeat" periódico que realiza reconhecimento facial
e de emoções a cada 5 minutos.

Endpoints principais:
- ``/voice`` (POST): recebe áudio gravado, devolve texto transcrito.
- ``/tts`` (POST): recebe texto, devolve áudio TTS.
- ``/heartbeat`` (GET): aciona reconhecimento facial/mood e retorna status.
"""

import os
import threading
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Configuração explícita de CORS para evitar bloqueios do navegador
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Configurações de ambiente
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
from openai import OpenAI
import ha_controller
import random

# Initialize client using OpenRouter (compatible with Gemini and OpenAI SDK)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=GEMINI_API_KEY
)

def load_soul():
    try:
        soul_path = os.path.join(os.path.dirname(__file__), "..", "referencias", "SOUL.md")
        if os.path.exists(soul_path):
            with open(soul_path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        print(f"Erro ao carregar SOUL.md: {e}")
    return "You are TARS, a dry-witted AI assistant. Humor setting: 75%."

SYSTEM_PROMPT = load_soul()

# Global state for simulated detection
_last_detection = {
    "face_detected": False,
    "mood": "neutral",
    "position": {"x": 0.5, "y": 0.5},
    "confidence": 0.0,
    "timestamp": 0
}

def facial_heartbeat() -> dict:
    """Executa reconhecimento facial e de emoções simulado."""
    global _last_detection
    detected = random.random() > 0.3
    if detected:
        _last_detection = {
            "face_detected": True,
            "mood": random.choice(["happy", "neutral", "surprised", "focused"]),
            "position": {
                "x": 0.5 + (random.random() - 0.5) * 0.2,
                "y": 0.5 + (random.random() - 0.5) * 0.2
            },
            "confidence": 0.8 + random.random() * 0.15,
            "timestamp": time.time()
        }
    else:
        _last_detection["face_detected"] = False
    return _last_detection

@app.route("/voice", methods=["POST"])
def voice_endpoint():
    """STT -> LLM -> TTS pipeline."""
    if 'audio' not in request.files:
        return jsonify({"error": "Nenhum áudio enviado"}), 400
    
    audio_file = request.files['audio']
    temp_path = os.path.join(os.path.dirname(__file__), "temp_voice.wav")
    audio_file.save(temp_path)

    try:
        # 1. Transcrição (Whisper)
        print(f"[face_server] Processando áudio...")
        try:
            transcript_resp = client.audio.transcriptions.create(model="openai/whisper-1", file=f)
            transcript = transcript_resp.text
        except Exception as e:
            print(f"❌ Erro no STT (Whisper): {e}")
            return jsonify({"error": "Falha na transcrição de voz. Verifique sua chave ou conexão."}), 500
            
        print(f"[face_server] Ouvido: {transcript}")

        # 2. Intenção e Chat
        response_text = ""
        txt = transcript.lower()
        if "ventilador" in txt or "fan" in txt:
            state = "off" if any(x in txt for x in ["desligar", "off", "parar"]) else "on"
            try: ha_controller.toggle_fan(state)
            except Exception as e: print(f"HA Fan Error: {e}")
            response_text = f"[neutral] Ventilador em modo {state.upper()}."
        elif "luz" in txt or "led" in txt:
            state = "off" if any(x in txt for x in ["desligar", "off", "apagar"]) else "on"
            try: ha_controller.toggle_room_led(state)
            except Exception as e: print(f"HA LED Error: {e}")
            response_text = f"[happy] Luz {state}."
        else:
            print(f"[face_server] Solicitando Gemini...")
            try:
                completion = client.chat.completions.create(
                    model="google/gemini-2.0-flash-001",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": transcript}
                    ],
                    max_tokens=150
                )
                response_text = completion.choices[0].message.content
            except Exception as e:
                print(f"❌ Erro no LLM (Gemini): {e}")
                return jsonify({"error": "O Gemini não conseguiu processar sua fala agora."}), 500

        # 3. TTS (Voz) - Opcional se falhar
        audio_data = None
        try:
            print(f"[face_server] Gerando áudio de resposta...")
            tts_resp = client.audio.speech.create(model="openai/tts-1", voice="onyx", input=response_text)
            audio_data = tts_resp.read()
        except Exception as e:
            print(f"⚠️ Aviso: Falha ao gerar voz (OpenRouter pode não suportar TTS direto): {e}")

        emotion = "neutral"
        if response_text.startswith("["):
            tag = response_text.split("]")[0][1:]
            if tag in ["happy", "curious", "surprised", "neutral", "thinking"]:
                emotion = tag

        # Se tiver áudio, devolve áudio. Se não, devolve JSON para o frontend lidar.
        if audio_data:
            from flask import make_response
            resp = make_response(audio_data)
            resp.headers['Content-Type'] = 'audio/mpeg'
            resp.headers['X-TARS-Transcript'] = transcript
            resp.headers['X-TARS-Response'] = response_text
            resp.headers['X-TARS-Emotion'] = emotion
            resp.headers['Access-Control-Expose-Headers'] = '*'
            return resp
        else:
            return jsonify({
                "transcript": transcript,
                "response": response_text,
                "emotion": emotion,
                "warning": "TTS_FAILED"
            })
        
        emotion = "neutral"
        if response_text.startswith("["):
            tag = response_text.split("]")[0][1:]
            if tag in ["happy", "curious", "surprised", "neutral", "thinking"]:
                emotion = tag

        # Devolver áudio binário com headers de metadados
        from flask import make_response
        resp = make_response(tts_resp.read())
        resp.headers['Content-Type'] = 'audio/mpeg'
        resp.headers['X-TARS-Transcript'] = transcript
        resp.headers['X-TARS-Response'] = response_text
        resp.headers['X-TARS-Emotion'] = emotion
        return resp

    except Exception as e:
        print(f"Erro no pipeline de voz: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_path): os.remove(temp_path)

@app.route("/text", methods=["POST"])
def text_endpoint():
    """Pipeline para comandos digitados no terminal."""
    data = request.json
    text = data.get("text", "").lower()
    
    if not text:
        return jsonify({"error": "Comando vazio"}), 400

    try:
        # Lógica de Intenção e Chat (Igual ao /voice)
        response_text = ""
        if "ventilador" in text or "fan" in text:
            state = "off" if any(x in text for x in ["desligar", "off", "parar"]) else "on"
            ha_controller.toggle_fan(state)
            response_text = f"[neutral] Ventilador {state.upper()}. Processamento concluído."
        elif "luz" in text or "led" in text:
            state = "off" if any(x in text for x in ["desligar", "off", "apagar"]) else "on"
            ha_controller.toggle_room_led(state)
            response_text = f"[happy] Luz {state}. Fótons ajustados."
        else:
            completion = client.chat.completions.create(
                model="google/gemini-2.0-flash-001",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": text}],
                max_tokens=150
            )
            response_text = completion.choices[0].message.content

        # Gera áudio para a resposta do terminal também
        tts_resp = client.audio.speech.create(model="openai/tts-1", voice="onyx", input=response_text)
        
        import base64
        audio_base64 = base64.b64encode(tts_resp.read()).decode('utf-8')

        return jsonify({
            "response": response_text,
            "audio": audio_base64,
            "emotion": "neutral" # Simplificado
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "online",
        "name": "TARS Vision Face Server",
        "model": "Gemini 2.0 Flash",
        "endpoints": ["/voice", "/tts", "/heartbeat"]
    })

@app.route("/heartbeat", methods=["GET"])
def heartbeat_endpoint():
    return jsonify(facial_heartbeat())

def run_server():
    # Alterado para 5117 para coincidir com o main.js
    port = int(os.getenv("FACE_SERVER_PORT", "5117"))
    print(f"🚀 TARS Face Server disparado na porta {port}")
    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    # Inicia o servidor Flask em thread separada
    threading.Thread(target=run_server, daemon=True).start()
    while True:
        time.sleep(60)
