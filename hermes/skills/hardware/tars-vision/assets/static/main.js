// main.js – TARS / MARK XXXV Core Interface
let scene, camera, renderer, rings = [];
const FACE_SERVER_URL = 'http://localhost:5117';

// Voice/PTT Setup
let mediaRecorder, audioChunks = [], isRecording = false;

function init() {
    const container = document.getElementById('canvas-container');
    
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 0, 15);

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    createJarvisHUD();
    initVoice();
    initWebcam();
    initClock();
    initTextInput();
    startHeartbeat();
    animate();
    
    addLogEntry("Sistemas de visão inicializados.", "sys");
}

function createJarvisHUD() {
    const ringCount = 6;
    const colors = [0x00d2ff, 0x3a7bd5, 0x00d2ff, 0x00ffff, 0x3a7bd5, 0xff0055];
    
    for (let i = 0; i < ringCount; i++) {
        const radius = 2 + i * 0.8;
        const segments = 64 + i * 16;
        const geometry = new THREE.RingGeometry(radius, radius + 0.08, segments, 1, 0, Math.PI * (0.8 + Math.random() * 1.2));
        const material = new THREE.MeshBasicMaterial({
            color: colors[i % colors.length],
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.5 - i * 0.05,
            blending: THREE.AdditiveBlending
        });
        const ring = new THREE.Mesh(geometry, material);
        ring.rotation.z = Math.random() * Math.PI;
        ring.userData.speed = (Math.random() - 0.5) * 0.015;
        scene.add(ring);
        rings.push(ring);
    }

    // Core Heart
    const coreGeom = new THREE.IcosahedronGeometry(1.2, 2);
    const coreMat = new THREE.MeshBasicMaterial({ 
        color: 0x00d2ff, 
        wireframe: true, 
        transparent: true, 
        opacity: 0.4 
    });
    const core = new THREE.Mesh(coreGeom, coreMat);
    core.name = "core";
    scene.add(core);
    rings.push(core);
}

function initClock() {
    const clockEl = document.getElementById('clock');
    setInterval(() => {
        const now = new Date();
        clockEl.textContent = now.toTimeString().split(' ')[0];
    }, 1000);
}

function addLogEntry(text, type = 'sys') {
    const terminal = document.getElementById('terminal');
    const entry = document.createElement('p');
    entry.className = type === 'sys' ? 'sys-msg' : 'user-msg';
    
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const prefix = type === 'sys' ? `[${time}] > ` : `[${time}] USER: `;
    
    entry.textContent = prefix + text;
    terminal.appendChild(entry);
    terminal.scrollTop = terminal.scrollHeight;
    
    if (terminal.children.length > 30) terminal.removeChild(terminal.firstChild);
}

function updateHUDStatus(emotion) {
    const emotionEl = document.getElementById('emotion-text');
    emotionEl.textContent = emotion.toUpperCase();
    
    // Mudar cor do core baseado na emoção
    const core = scene.getObjectByName("core");
    if (core) {
        if (emotion === "happy") core.material.color.setHex(0x00ff88);
        else if (emotion === "surprised") core.material.color.setHex(0xffaa00);
        else if (emotion === "thinking") core.material.color.setHex(0xaa00ff);
        else core.material.color.setHex(0x00d2ff);
    }
}

function initVoice() {
    const pttBtn = document.getElementById('ptt-btn');
    if (!pttBtn) return;

    pttBtn.addEventListener('mousedown', async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
            mediaRecorder.onstop = sendAudioData;
            mediaRecorder.start();
            isRecording = true;
            pttBtn.classList.add('recording');
            pttBtn.querySelector('.icon').textContent = "🔴";
            document.getElementById('status-text').textContent = "LISTENING...";
        } catch (err) {
            addLogEntry("Erro ao acessar microfone.", "sys");
        }
    });

    pttBtn.addEventListener('mouseup', () => {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            isRecording = false;
            pttBtn.classList.remove('recording');
            pttBtn.querySelector('.icon').textContent = "🎤";
            document.getElementById('status-text').textContent = "THINKING...";
            mediaRecorder.stream.getTracks().forEach(t => t.stop());
        }
    });
}

function initWebcam() {
    const enableCamBtn = document.getElementById('enable-cam');
    enableCamBtn.addEventListener('click', async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            const video = document.getElementById('webcam');
            video.srcObject = stream;
            enableCamBtn.innerHTML = '<span class="icon">✓</span> VISION ACTIVE';
            enableCamBtn.style.borderColor = "#00ff88";
            addLogEntry("Fluxo de vídeo estabelecido.", "sys");
        } catch (err) {
            addLogEntry("Falha na inicialização da visão.", "sys");
        }
    });
}

function initTextInput() {
    const input = document.getElementById('command-input');
    input.addEventListener('keypress', async (e) => {
        if (e.key === 'Enter' && input.value.trim()) {
            const text = input.value;
            input.value = '';
            addLogEntry(text, 'user');
            await sendTextCommand(text);
        }
    });
}

async function sendTextCommand(text) {
    try {
        document.getElementById('status-text').textContent = "THINKING...";
        const response = await fetch(`${FACE_SERVER_URL}/text`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        const data = await response.json();
        
        addLogEntry(data.response, 'sys');
        document.getElementById('status-text').textContent = "IDLE";
        
        if (data.audio) {
            const audio = new Audio("data:audio/mp3;base64," + data.audio);
            audio.play();
        }
        updateHUDStatus(data.emotion || 'neutral');
    } catch (err) {
        addLogEntry("Erro de conexão com o terminal.", "sys");
    }
}

async function sendAudioData() {
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
    const formData = new FormData();
    formData.append('audio', audioBlob, 'voice.wav');

    try {
        const response = await fetch(`${FACE_SERVER_URL}/voice`, { method: 'POST', body: formData });
        if (!response.ok) throw new Error("Erro no servidor");

        const blob = await response.blob();
        const audio = new Audio(URL.createObjectURL(blob));
        
        const transcript = response.headers.get('X-TARS-Transcript');
        const respText = response.headers.get('X-TARS-Response');
        const emotion = response.headers.get('X-TARS-Emotion') || 'neutral';
        
        addLogEntry(respText, 'sys');
        updateHUDStatus(emotion);
        document.getElementById('status-text').textContent = "IDLE";
        
        audio.play();
    } catch (err) {
        addLogEntry("Erro na comunicação com o Core.", "sys");
        document.getElementById('status-text').textContent = "ERROR";
    }
}

async function startHeartbeat() {
    setInterval(async () => {
        try {
            const response = await fetch(`${FACE_SERVER_URL}/heartbeat`);
            const data = await response.json();
            if (data.face_detected) {
                updateHUDStatus(data.mood);
            }
        } catch (err) {}
    }, 5000);
}

function animate() {
    requestAnimationFrame(animate);
    rings.forEach((ring) => {
        if (ring.name === "core") {
            ring.rotation.x += 0.01;
            ring.rotation.y += 0.01;
            const pulse = 1 + Math.sin(Date.now() * 0.003) * 0.1;
            ring.scale.set(pulse, pulse, pulse);
        } else {
            ring.rotation.z += ring.userData.speed;
            ring.rotation.x += ring.userData.speed * 0.5;
        }
    });
    renderer.render(scene, camera);
}

window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

init();
