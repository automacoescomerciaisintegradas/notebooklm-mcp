# TARS Vision — Hardware Setup & Firmware

## Hardware Requirements
- **Raspberry Pi 5** (8GB recommended for Whisper/Local AI).
- **HuskyLens** (AI Camera) connected via I2C (Bus 1, addr 0x10).
- **DSI Touchscreen** (800x480) for the animated face.
- **USB/HAT Microphone** for voice capture.
- **External Speaker** (3.5mm jack or USB).

## Wiring (I2C)
| HuskyLens Pin | RPi 5 Pin | Color |
|---|---|---|
| VCC | 5V (Pin 2) | Red |
| GND | GND (Pin 6) | Black |
| SDA | SDA (Pin 3) | Green |
| SCL | SCL (Pin 5) | Blue |

## Software Setup
1. **Enable I2C**:
   ```bash
   sudo raspi-config  # Interface Options -> I2C -> Enable
   ```
2. **Install Dependencies**:
   ```bash
   pip install flask flask-cors requests smbus2 openai-whisper openai
   ```
3. **Environment variables**:
   Configure `.env` with `OPENAI_API_KEY`, `HOME_ASSISTANT_URL`, and `HOME_ASSISTANT_TOKEN`.

## Kiosk Mode (Facial Screen)
To launch the Three.js frontend as a standalone app on the DSI screen:
```bash
chromium-browser --kiosk --app=http://localhost:5117/tars
```
