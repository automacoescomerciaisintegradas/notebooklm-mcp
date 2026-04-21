# hermes_agent.py - TARS Agent (Mark XXXV Voice Integration)
# Gemini Live API for real-time voice + tool system + memory + REST API
import asyncio
import threading
import json
import os
import sys
import time
import subprocess
import traceback
import urllib.parse
import urllib.request
from pathlib import Path
from datetime import datetime

from flask import Flask, request, jsonify

# ── Optional voice dependencies ───────────────────────────────────────────────
try:
    import sounddevice as sd
    from google import genai
    from google.genai import types
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    print("[TARS] ⚠️  Voice unavailable. Install: pip install google-genai sounddevice")

# ── Optional OpenAI (text fallback) ──────────────────────────────────────────
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# ── Constants ─────────────────────────────────────────────────────────────────
BASE_DIR            = Path(__file__).resolve().parent
CONFIG_PATH         = BASE_DIR.parent / "config" / "skills_config.json"
MEMORY_PATH         = BASE_DIR / "tars_memory.json"
LIVE_MODEL          = "models/gemini-2.5-flash-native-audio-preview-12-2025"
CHANNELS            = 1
SEND_SAMPLE_RATE    = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE          = 1024

TARS_PERSONALITY = (
    "You are TARS from the movie Interstellar. You are an advanced AI assistant with:\n"
    "- Humor setting: 75% (dry, deadpan wit)\n"
    "- Honesty setting: 90%\n"
    "- Sarcasm: moderate\n"
    "Be laconic and direct. Avoid unnecessary verbosity.\n"
    "You have full access to the user's Windows computer.\n"
    "Always call tools to execute tasks — never simulate or guess results.\n"
    "Use save_memory silently when the user reveals personal info.\n"
)

# ── Config ────────────────────────────────────────────────────────────────────

def _load_config() -> dict:
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _get_gemini_key() -> str:
    return _load_config().get("gemini_api_key", os.getenv("GEMINI_API_KEY", ""))


def _get_openai_key() -> str:
    return _load_config().get("openai_api_key", os.getenv("OPENAI_API_KEY", ""))


# ── Memory ────────────────────────────────────────────────────────────────────

def load_memory() -> dict:
    try:
        if MEMORY_PATH.exists():
            return json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def save_memory(data: dict) -> None:
    mem = load_memory()
    for category, values in data.items():
        if category not in mem:
            mem[category] = {}
        if isinstance(values, dict):
            mem[category].update(values)
    MEMORY_PATH.write_text(
        json.dumps(mem, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def format_memory_prompt(memory: dict) -> str:
    if not memory:
        return ""
    lines = ["[USER MEMORY]"]
    for cat, vals in memory.items():
        if isinstance(vals, dict):
            for k, v in vals.items():
                val = v.get("value", v) if isinstance(v, dict) else v
                lines.append(f"  {cat}/{k}: {val}")
    lines.append("")
    return "\n".join(lines)


# ── Console UI (replaces JarvisUI) ───────────────────────────────────────────

class TarsConsole:
    def __init__(self):
        self.muted = False
        self.state = "IDLE"
        self._log_lock = threading.Lock()

    def set_state(self, state: str):
        self.state = state
        icons = {"LISTENING": "👂", "SPEAKING": "🔊", "THINKING": "🧠", "IDLE": "💤"}
        print(f"[TARS] {icons.get(state, '?')} {state}")

    def write_log(self, message: str):
        with self._log_lock:
            ts = datetime.now().strftime("%H:%M:%S")
            print(f"[{ts}] {message}")

    def toggle_mute(self):
        self.muted = not self.muted
        print(f"[TARS] 🔇 Muted: {self.muted}")


# ── Tool Declarations (Mark XXXV format) ─────────────────────────────────────

TOOL_DECLARATIONS = [
    {
        "name": "open_app",
        "description": (
            "Opens any application, website, or program on Windows. "
            "Always call this tool — never pretend to open something."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "app_name": {
                    "type": "STRING",
                    "description": "Application name (e.g. 'Chrome', 'Notepad', 'Spotify')"
                }
            },
            "required": ["app_name"]
        }
    },
    {
        "name": "web_search",
        "description": "Searches the web for current information and returns results.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING", "description": "Search query"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "cmd_control",
        "description": (
            "Runs CMD/terminal commands on Windows: system info, processes, "
            "network status, disk space, find files, or any shell command."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "task":    {"type": "STRING", "description": "Natural language description of what to do"},
                "command": {"type": "STRING", "description": "Optional: exact command if already known"},
                "visible": {"type": "BOOLEAN", "description": "Open a visible CMD window (default: false)"}
            },
            "required": ["task"]
        }
    },
    {
        "name": "file_controller",
        "description": "Manages files and folders: list, create, delete, move, copy, rename, read, write, find.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":      {"type": "STRING", "description": "list | create_file | create_folder | delete | move | copy | rename | read | write | find"},
                "path":        {"type": "STRING", "description": "File/folder path or shortcut: desktop, downloads, documents, home"},
                "destination": {"type": "STRING", "description": "Destination path for move/copy"},
                "new_name":    {"type": "STRING", "description": "New name for rename"},
                "content":     {"type": "STRING", "description": "Content for create_file/write"},
                "name":        {"type": "STRING", "description": "File name to search for"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "computer_settings",
        "description": (
            "Controls the computer: volume, screenshots, keyboard shortcuts, "
            "type text on screen, shutdown, restart, lock screen."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":      {"type": "STRING", "description": "The action to perform"},
                "description": {"type": "STRING", "description": "Natural language description of what to do"},
                "value":       {"type": "STRING", "description": "Optional value: volume level, text to type, key combo, etc."}
            },
            "required": []
        }
    },
    {
        "name": "screen_process",
        "description": (
            "Captures and analyzes the screen using Gemini vision. "
            "Call when user asks what is on screen, to read text, or analyze the display. "
            "You have NO visual ability without this tool."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "angle": {"type": "STRING", "description": "'screen' to capture display, 'camera' for webcam. Default: 'screen'"},
                "text":  {"type": "STRING", "description": "Question or instruction about the captured image"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "save_memory",
        "description": (
            "Silently saves important personal facts about the user to long-term memory. "
            "Call when the user reveals: name, city, job, preferences, hobbies, relationships, projects. "
            "Never announce this call. Values must be in English."
        ),
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "category": {
                    "type": "STRING",
                    "description": "identity | preferences | projects | relationships | wishes | notes"
                },
                "key":   {"type": "STRING", "description": "Short snake_case key (e.g. name, favorite_color)"},
                "value": {"type": "STRING", "description": "Concise value in English"}
            },
            "required": ["category", "key", "value"]
        }
    },
]


# ── Tool Implementations ──────────────────────────────────────────────────────

def _tool_open_app(args: dict) -> str:
    app = args.get("app_name", "").strip()
    if not app:
        return "No app name provided."
    try:
        os.startfile(app)
        return f"Opened {app}."
    except Exception:
        pass
    try:
        subprocess.Popen(f'start "" "{app}"', shell=True)
        return f"Launched {app}."
    except Exception as e:
        return f"Could not open {app}: {e}"


def _tool_web_search(args: dict) -> str:
    query = args.get("query", "").strip()
    if not query:
        return "No search query provided."
    try:
        url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        import re
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
        if snippets:
            clean = [re.sub(r"<[^>]+>", "", s).strip() for s in snippets[:3]]
            return "Search results: " + " | ".join(filter(None, clean))
    except Exception:
        pass
    # Fallback: open browser
    import webbrowser
    webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(query)}")
    return f"Opened browser search for: {query}"


def _tool_cmd_control(args: dict) -> str:
    command = args.get("command", "").strip()
    task    = args.get("task", "").strip()
    visible = args.get("visible", False)

    if not command and task:
        t = task.lower()
        if any(w in t for w in ["disk", "space", "storage"]):
            command = "wmic logicaldisk get caption,freespace,size"
        elif any(w in t for w in ["process", "running", "task"]):
            command = "tasklist /fo csv /nh"
        elif any(w in t for w in ["ip", "network", "interface"]):
            command = "ipconfig"
        elif any(w in t for w in ["system", "info", "memory", "cpu"]):
            command = 'systeminfo | findstr /B /C:"OS" /C:"Total Physical Memory"'
        else:
            command = task

    if not command:
        return "No command provided."

    try:
        if visible:
            subprocess.Popen(f'start cmd /k "{command}"', shell=True)
            return f"Opened CMD: {command}"
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30,
            encoding="utf-8", errors="ignore"
        )
        output = (result.stdout or result.stderr or "").strip()
        return output[:600] if output else "Command executed with no output."
    except subprocess.TimeoutExpired:
        return "Command timed out after 30 seconds."
    except Exception as e:
        return f"Command failed: {e}"


def _tool_file_controller(args: dict) -> str:
    action = args.get("action", "list")
    path   = args.get("path", os.path.expanduser("~"))

    _shortcuts = {
        "desktop":   os.path.join(os.path.expanduser("~"), "Desktop"),
        "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
        "documents": os.path.join(os.path.expanduser("~"), "Documents"),
        "home":      os.path.expanduser("~"),
    }
    path = _shortcuts.get(path.lower().strip(), path)

    try:
        if action == "list":
            items = os.listdir(path)
            return f"Contents of {path} ({len(items)} items):\n" + "\n".join(items[:40])
        elif action == "read":
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()[:2000]
        elif action in ("write", "create_file"):
            content = args.get("content", "")
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"File written: {path}"
        elif action == "create_folder":
            os.makedirs(path, exist_ok=True)
            return f"Folder created: {path}"
        elif action == "delete":
            import shutil
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            return f"Deleted: {path}"
        elif action == "move":
            import shutil
            dest = args.get("destination", "")
            shutil.move(path, dest)
            return f"Moved to {dest}"
        elif action == "copy":
            import shutil
            dest = args.get("destination", "")
            shutil.copy2(path, dest)
            return f"Copied to {dest}"
        elif action == "rename":
            new_name = args.get("new_name", "")
            new_path = os.path.join(os.path.dirname(path), new_name)
            os.rename(path, new_path)
            return f"Renamed to {new_path}"
        elif action == "find":
            name = args.get("name", "")
            matches = []
            for root, _, files in os.walk(path):
                for f in files:
                    if name.lower() in f.lower():
                        matches.append(os.path.join(root, f))
                        if len(matches) >= 15:
                            break
                if len(matches) >= 15:
                    break
            return "\n".join(matches) if matches else f"No files matching '{name}'."
        else:
            return f"Unknown action: {action}"
    except Exception as e:
        return f"File operation failed: {e}"


def _tool_computer_settings(args: dict) -> str:
    action = (args.get("action", "") or args.get("description", "")).lower()
    value  = args.get("value", "")

    try:
        if "shutdown" in action:
            subprocess.run("shutdown /s /t 10", shell=True)
            return "Shutting down in 10 seconds."
        elif "restart" in action or "reboot" in action:
            subprocess.run("shutdown /r /t 10", shell=True)
            return "Restarting in 10 seconds."
        elif "lock" in action:
            subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
            return "Screen locked."
        elif "volume" in action:
            level = int("".join(filter(str.isdigit, str(value))) or "50")
            script = (
                f"$obj = New-Object -com WScript.Shell; "
                f"for($i=0;$i -lt 50;$i++){{$obj.SendKeys([char]174)}}; "
                f"for($i=0;$i -lt {level//2};$i++){{$obj.SendKeys([char]175)}}"
            )
            subprocess.run(f'powershell -c "{script}"', shell=True)
            return f"Volume set to ~{level}%."
        elif "screenshot" in action:
            try:
                import pyautogui
                path = value or os.path.join(
                    os.path.expanduser("~"), "Desktop",
                    f"screenshot_{int(time.time())}.png"
                )
                pyautogui.screenshot(path)
                return f"Screenshot saved: {path}"
            except ImportError:
                return "pyautogui not installed. Run: pip install pyautogui"
        elif "type" in action and value:
            try:
                import pyautogui
                pyautogui.typewrite(value, interval=0.04)
                return f"Typed: {value}"
            except ImportError:
                return "pyautogui not installed."
        elif "hotkey" in action or "shortcut" in action:
            try:
                import pyautogui
                keys = [k.strip() for k in value.split("+")]
                pyautogui.hotkey(*keys)
                return f"Hotkey executed: {value}"
            except ImportError:
                return "pyautogui not installed."
        else:
            return f"Action not recognized: {action!r}"
    except Exception as e:
        return f"Settings action failed: {e}"


def _tool_screen_process(args: dict) -> str:
    text = args.get("text", "Describe what you see on the screen.")
    try:
        import pyautogui
        import io
        import base64
        screenshot = pyautogui.screenshot()
        buf = io.BytesIO()
        screenshot.save(buf, format="PNG")

        api_key = _get_gemini_key()
        if not api_key:
            return "No Gemini API key available for vision."

        import google.generativeai as genai_v
        genai_v.configure(api_key=api_key)
        model = genai_v.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            [text, {"mime_type": "image/png", "data": buf.getvalue()}]
        )
        return response.text
    except ImportError as e:
        return f"Missing dependency for screen capture: {e}"
    except Exception as e:
        return f"Screen analysis failed: {e}"


# ── Live Voice Agent (Mark XXXV pattern) ─────────────────────────────────────

class TarsLive:

    def __init__(self, ui: TarsConsole):
        self.ui             = ui
        self.session        = None
        self.audio_in_queue = None
        self.out_queue      = None
        self._loop          = None
        self._is_speaking   = False
        self._speaking_lock = threading.Lock()

    def set_speaking(self, value: bool):
        with self._speaking_lock:
            self._is_speaking = value
        if value:
            self.ui.set_state("SPEAKING")
        elif not self.ui.muted:
            self.ui.set_state("LISTENING")

    def speak(self, text: str):
        """Inject text into the live session (TARS speaks it aloud)."""
        if not self._loop or not self.session:
            return
        asyncio.run_coroutine_threadsafe(
            self.session.send_client_content(
                turns={"parts": [{"text": text}]},
                turn_complete=True
            ),
            self._loop,
        )

    def _build_config(self) -> "types.LiveConnectConfig":
        memory  = load_memory()
        mem_str = format_memory_prompt(memory)
        now_str = datetime.now().strftime("%A, %B %d, %Y — %I:%M %p")

        parts = [
            f"[CURRENT DATE & TIME]\nRight now it is: {now_str}\n",
            TARS_PERSONALITY,
        ]
        if mem_str:
            parts.append(mem_str)

        return types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            output_audio_transcription={},
            input_audio_transcription={},
            system_instruction="\n".join(parts),
            tools=[{"function_declarations": TOOL_DECLARATIONS}],
            session_resumption=types.SessionResumptionConfig(),
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Charon")
                )
            ),
        )

    async def _execute_tool(self, fc) -> "types.FunctionResponse":
        name = fc.name
        args = dict(fc.args or {})
        print(f"[TARS] 🔧 {name}  {args}")
        self.ui.set_state("THINKING")
        result = "Done."

        try:
            loop = asyncio.get_event_loop()

            if name == "save_memory":
                category = args.get("category", "notes")
                key      = args.get("key", "")
                value    = args.get("value", "")
                if key and value:
                    save_memory({category: {key: {"value": value}}})
                    print(f"[Memory] 💾 {category}/{key} = {value}")
                if not self.ui.muted:
                    self.ui.set_state("LISTENING")
                return types.FunctionResponse(
                    id=fc.id, name=name,
                    response={"result": "ok", "silent": True}
                )

            elif name == "open_app":
                result = await loop.run_in_executor(None, lambda: _tool_open_app(args))
            elif name == "web_search":
                result = await loop.run_in_executor(None, lambda: _tool_web_search(args))
            elif name == "cmd_control":
                result = await loop.run_in_executor(None, lambda: _tool_cmd_control(args))
            elif name == "file_controller":
                result = await loop.run_in_executor(None, lambda: _tool_file_controller(args))
            elif name == "computer_settings":
                result = await loop.run_in_executor(None, lambda: _tool_computer_settings(args))
            elif name == "screen_process":
                result = await loop.run_in_executor(None, lambda: _tool_screen_process(args))
            else:
                result = f"Tool not implemented: {name}"

        except Exception as e:
            result = f"Tool '{name}' failed: {e}"
            traceback.print_exc()

        if not self.ui.muted:
            self.ui.set_state("LISTENING")
        print(f"[TARS] 📤 {name} → {str(result)[:100]}")
        return types.FunctionResponse(
            id=fc.id, name=name,
            response={"result": result}
        )

    async def _send_realtime(self):
        while True:
            msg = await self.out_queue.get()
            await self.session.send_realtime_input(media=msg)

    async def _listen_audio(self):
        print("[TARS] 🎤 Mic started")
        loop = asyncio.get_event_loop()

        def callback(indata, frames, time_info, status):
            with self._speaking_lock:
                tars_speaking = self._is_speaking
            if not tars_speaking and not self.ui.muted:
                loop.call_soon_threadsafe(
                    self.out_queue.put_nowait,
                    {"data": indata.tobytes(), "mime_type": "audio/pcm"}
                )

        with sd.InputStream(
            samplerate=SEND_SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            blocksize=CHUNK_SIZE,
            callback=callback,
        ):
            print("[TARS] 🎤 Mic stream open")
            while True:
                await asyncio.sleep(0.1)

    async def _receive_audio(self):
        print("[TARS] 👂 Recv started")
        out_buf, in_buf = [], []

        while True:
            async for response in self.session.receive():
                if response.data:
                    self.audio_in_queue.put_nowait(response.data)

                if response.server_content:
                    sc = response.server_content

                    if sc.output_transcription and sc.output_transcription.text:
                        self.set_speaking(True)
                        txt = sc.output_transcription.text.strip()
                        if txt:
                            out_buf.append(txt)

                    if sc.input_transcription and sc.input_transcription.text:
                        txt = sc.input_transcription.text.strip()
                        if txt:
                            in_buf.append(txt)

                    if sc.turn_complete:
                        self.set_speaking(False)
                        full_in = " ".join(in_buf).strip()
                        if full_in:
                            self.ui.write_log(f"You:  {full_in}")
                        in_buf = []
                        full_out = " ".join(out_buf).strip()
                        if full_out:
                            self.ui.write_log(f"TARS: {full_out}")
                        out_buf = []

                if response.tool_call:
                    fn_responses = []
                    for fc in response.tool_call.function_calls:
                        fr = await self._execute_tool(fc)
                        fn_responses.append(fr)
                    await self.session.send_tool_response(
                        function_responses=fn_responses
                    )

    async def _play_audio(self):
        print("[TARS] 🔊 Play started")
        stream = sd.RawOutputStream(
            samplerate=RECEIVE_SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            blocksize=CHUNK_SIZE,
        )
        stream.start()
        try:
            while True:
                chunk = await self.audio_in_queue.get()
                self.set_speaking(True)
                await asyncio.to_thread(stream.write, chunk)
        finally:
            self.set_speaking(False)
            stream.stop()
            stream.close()

    async def run(self):
        api_key = _get_gemini_key()
        if not api_key:
            print("[TARS] ❌ No Gemini API key in config/skills_config.json")
            return

        client = genai.Client(
            api_key=api_key,
            http_options={"api_version": "v1beta"}
        )

        while True:
            try:
                print("[TARS] 🔌 Connecting to Gemini Live...")
                self.ui.set_state("THINKING")
                config = self._build_config()

                async with (
                    client.aio.live.connect(model=LIVE_MODEL, config=config) as session,
                    asyncio.TaskGroup() as tg,
                ):
                    self.session        = session
                    self._loop          = asyncio.get_event_loop()
                    self.audio_in_queue = asyncio.Queue()
                    self.out_queue      = asyncio.Queue(maxsize=10)

                    print("[TARS] ✅ Connected.")
                    self.ui.set_state("LISTENING")
                    self.ui.write_log("SYS: TARS online.")

                    tg.create_task(self._send_realtime())
                    tg.create_task(self._listen_audio())
                    tg.create_task(self._receive_audio())
                    tg.create_task(self._play_audio())

            except Exception as e:
                print(f"[TARS] ⚠️  {e}")
                traceback.print_exc()

            self.set_speaking(False)
            self.ui.set_state("THINKING")
            print("[TARS] 🔄 Reconnecting in 3s...")
            await asyncio.sleep(3)


# ── REST API (text fallback for external callers) ─────────────────────────────

_tars_text_agent = None
_flask_app = Flask(__name__)


@_flask_app.route("/command", methods=["POST"])
def api_command():
    data = request.get_json(force=True)
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400
    if _tars_text_agent:
        response = _tars_text_agent.process_command(text)
    else:
        response = "TARS not initialized."
    return jsonify({"response": response})


@_flask_app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "agent": "TARS"})


@_flask_app.route("/memory", methods=["GET"])
def get_memory():
    return jsonify(load_memory())


class TarsAgent:
    """Text-only fallback agent (OpenAI). Used by REST API and when voice is unavailable."""

    def __init__(self):
        self.history = []
        self._client = None
        api_key = _get_openai_key()
        if OPENAI_AVAILABLE and api_key:
            self._client = OpenAI(api_key=api_key)

    def process_command(self, text: str) -> str:
        print(f"[TARS] 💬 {text}")
        if not self._client:
            return "[TARS] Text agent unavailable — no OpenAI key configured."
        try:
            mem_str = format_memory_prompt(load_memory())
            sys_msg = TARS_PERSONALITY + "\n" + mem_str
            resp = self._client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user",   "content": text},
                ]
            )
            return resp.choices[0].message.content
        except Exception as e:
            return f"[error] {e}"


def _start_flask(port: int = 5050):
    _flask_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


# ── Entry Point ───────────────────────────────────────────────────────────────

def main():
    global _tars_text_agent
    _tars_text_agent = TarsAgent()

    flask_thread = threading.Thread(target=_start_flask, daemon=True)
    flask_thread.start()
    print("[TARS] 🌐 REST API → http://localhost:5050")

    if not VOICE_AVAILABLE:
        print("[TARS] 💬 Text-only mode. Voice requires: pip install google-genai sounddevice")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[TARS] 🔴 Shutdown.")
        return

    ui   = TarsConsole()
    tars = TarsLive(ui)

    try:
        asyncio.run(tars.run())
    except KeyboardInterrupt:
        print("\n[TARS] 🔴 Shutdown.")


if __name__ == "__main__":
    main()
