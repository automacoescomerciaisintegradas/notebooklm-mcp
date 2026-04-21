# SKILL.md

## Manifesto de habilidades de Hermes

- **Nome:** tars-vision
- **Categoria:** hardware
- **Descrição:** Rosto holográfico em tela DSI 800x480 com animações Three.js, captura de áudio via toque, reconhecimento de gestos HuskyLens e integração opcional ao Home Assistant. Inclui heartbeat de reconhecimento facial e emocional.
- **Autor:** @MayukhBuilds
- **Versão:** 1.0.0
- **Licença:** MIT
- **Dependências:**
  - Python 3.10+
  - `whisper` (OpenAI Whisper)
  - `openai` (para TTS)
  - `huskylens` (driver I2C)
  - `three.js` (frontend holográfico)
- **Entry point:** `run.ps1` (PowerShell) ou `run.sh` (Unix)
- **Tags:** hermes, tars, huskylens, home-assistant, threejs, raspberry-pi

## Estrutura de arquivos
```
hermes/skills/hardware/tars-vision/
│   SKILL.md
│   run.ps1   # script de inicialização para Windows
│   run.sh    # script de inicialização para Unix (opcional)
│   manifest.json
│
├── assets/
│   ├── face_server.py
│   ├── vision_router.py
│   ├── huskylens_uart.py
│   ├── gesture_classifier.py
│   ├── ha_controller.py
│   └── static/   # Three.js frontend
│       └── index.html
│
└── referencias/
    ├── SOUL.md
    ├── SETUP.md
    └── ARCHITECTURE.md
```

---

## Recursos Principais
- 👽 **Rosto Holográfico**: Interface 3D (Three.js) com suporte a GLB e animações faciais.
- 🖐️ **Controle Gestual**: Integração HuskyLens para gerenciar dispositivos via gesto.
- 🎙️ **Voz TARS**: Personalidade sarcástica (Humor 75%) baseada no filme Interstellar.
- 💓 **Heartbeat Visual**: Sincronização em tempo-real entre detecção física e interface web.

## Configuração de Personalidade
A inteligência do TARS é guiada pelo arquivo `referencias/SOUL.md`. Ele responderá sempre com tags de emoção como `[happy]` ou `[thinking]`, que podem ser lidas pelo frontend para transições de animação.

---
*Construído para Mayukh (@MayukhBuilds) — Radioastronomia e Automação.*
