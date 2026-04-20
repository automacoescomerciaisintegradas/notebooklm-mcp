/**
 * NotebookLM MCP Server Manager — Web App JS
 * (c) Automacoes Comerciais Integradas 2026
 */

const API = '';
let refreshTimer = null;

// === Init ===
document.addEventListener('DOMContentLoaded', () => {
    refreshServers();
    refreshHealth();
    refreshSecurity();
    refreshClients();

    // Auto-refresh a cada 4s
    refreshTimer = setInterval(() => {
        refreshServers();
        refreshHealth();
    }, 4000);
});

// === Tab Navigation ===
function switchTab(tab) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));

    document.getElementById(`tab-${tab}`).classList.add('active');
    document.querySelector(`[data-tab="${tab}"]`).classList.add('active');

    if (tab === 'security') refreshSecurity();
    if (tab === 'clients') refreshClients();
    if (tab === 'logs') populateLogSelect();
}

// === Servers ===
async function refreshServers() {
    try {
        const res = await fetch(`${API}/api/servers`);
        const data = await res.json();
        renderServers(data.servers);
        document.getElementById('totalServers').textContent = data.count;
        const running = data.servers.filter(s => s.running).length;
        document.getElementById('runningServers').textContent = running;
    } catch (e) {
        console.error('Erro ao carregar servidores:', e);
    }
}

function renderServers(servers) {
    const grid = document.getElementById('serverGrid');

    if (!servers.length) {
        grid.innerHTML = `
            <div class="empty-state">
                <p>Nenhum servidor configurado.</p>
                <p class="text-muted">Clique em "+ Adicionar" para registrar um servidor MCP.</p>
            </div>`;
        return;
    }

    grid.innerHTML = servers.map(s => `
        <div class="server-card">
            <div class="server-card-header">
                <span class="server-name">${esc(s.name)}</span>
                <span class="status-badge ${s.running ? 'status-running' : 'status-stopped'}">
                    <span class="dot ${s.running ? 'dot-ok' : 'dot-err'}"></span>
                    ${s.running ? 'Rodando' : 'Parado'}
                </span>
            </div>
            <div class="server-details">
                <span class="detail-label">Comando</span>
                <span class="detail-value">${esc(s.command || '-')}</span>
                <span class="detail-label">Transporte</span>
                <span class="detail-value">${esc(s.transport || 'stdio')}</span>
                <span class="detail-label">Porta</span>
                <span class="detail-value">${s.port || '-'}</span>
                <span class="detail-label">PID</span>
                <span class="detail-value">${s.pid || '-'}</span>
            </div>
            <div class="server-actions">
                ${s.running
                    ? `<button class="btn btn-danger btn-sm" onclick="stopServer('${esc(s.name)}')">Parar</button>
                       <button class="btn btn-warning btn-sm" onclick="restartServer('${esc(s.name)}')">Reiniciar</button>`
                    : `<button class="btn btn-success btn-sm" onclick="startServer('${esc(s.name)}')">Iniciar</button>`
                }
                <button class="btn btn-ghost btn-sm" onclick="viewServerLogs('${esc(s.name)}')">Logs</button>
                <button class="btn btn-ghost btn-sm" onclick="removeServer('${esc(s.name)}')">Remover</button>
            </div>
        </div>
    `).join('');
}

async function startServer(name) {
    const res = await fetch(`${API}/api/servers/${encodeURIComponent(name)}/start`, { method: 'POST' });
    const data = await res.json();
    toast(data.success ? 'success' : 'error', data.message || data.error);
    refreshServers();
}

async function stopServer(name) {
    const res = await fetch(`${API}/api/servers/${encodeURIComponent(name)}/stop`, { method: 'POST' });
    const data = await res.json();
    toast(data.success ? 'success' : 'error', data.message || data.error);
    refreshServers();
}

async function restartServer(name) {
    const res = await fetch(`${API}/api/servers/${encodeURIComponent(name)}/restart`, { method: 'POST' });
    const data = await res.json();
    toast(data.success ? 'success' : 'error', data.message || data.error);
    refreshServers();
}

async function removeServer(name) {
    if (!confirm(`Remover servidor "${name}"?`)) return;
    const res = await fetch(`${API}/api/servers/${encodeURIComponent(name)}`, { method: 'DELETE' });
    const data = await res.json();
    toast(data.success ? 'success' : 'error', data.message || data.error);
    refreshServers();
}

function viewServerLogs(name) {
    switchTab('logs');
    const select = document.getElementById('logServerSelect');
    select.value = name;
    loadLogs();
}

// === Add Server Modal ===
function showAddServerModal() {
    document.getElementById('addServerModal').classList.add('show');
    document.getElementById('addName').focus();
}

function hideAddServerModal() {
    document.getElementById('addServerModal').classList.remove('show');
}

function closeModal(event) {
    if (event.target === event.currentTarget) {
        hideAddServerModal();
    }
}

async function addServer() {
    const name = document.getElementById('addName').value.trim();
    const command = document.getElementById('addCommand').value.trim();
    const transport = document.getElementById('addTransport').value;
    const port = document.getElementById('addPort').value.trim();
    const argsStr = document.getElementById('addArgs').value.trim();

    if (!name) { toast('error', 'Nome e obrigatorio'); return; }

    const body = {
        name,
        command: command || 'nlm',
        transport,
        args: argsStr ? argsStr.split(' ') : [],
    };
    if (port) body.port = parseInt(port);

    const res = await fetch(`${API}/api/servers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });
    const data = await res.json();

    if (data.success) {
        toast('success', data.message);
        hideAddServerModal();
        // Limpar form
        document.getElementById('addName').value = '';
        document.getElementById('addArgs').value = '';
        document.getElementById('addPort').value = '';
        refreshServers();
    } else {
        toast('error', data.error);
    }
}

// === Health ===
async function refreshHealth() {
    try {
        const res = await fetch(`${API}/api/health`);
        const data = await res.json();
        const badge = document.getElementById('healthBadge');
        const text = document.getElementById('healthText');
        const dot = badge.querySelector('.dot');

        dot.className = 'dot dot-ok';
        text.textContent = `${data.servers_running}/${data.servers_total} rodando`;
    } catch (e) {
        const badge = document.getElementById('healthBadge');
        const text = document.getElementById('healthText');
        const dot = badge.querySelector('.dot');
        dot.className = 'dot dot-err';
        text.textContent = 'Offline';
    }
}

// === Security ===
async function refreshSecurity() {
    try {
        const res = await fetch(`${API}/api/security/status`);
        const data = await res.json();

        document.getElementById('securityPatterns').textContent = data.pattern_count;
        document.getElementById('secEnabled').textContent = data.enabled ? 'ATIVO' : 'OFF';
        document.getElementById('secPatterns').textContent = data.pattern_count;
        document.getElementById('secViolations').textContent = data.violation_count;

        const secBadge = document.getElementById('securityBadge');
        secBadge.className = `security-badge ${data.enabled ? 'active' : ''}`;

        // Violations list
        const list = document.getElementById('violationsList');
        const recent = data.summary.recent || [];
        if (recent.length) {
            list.innerHTML = '<h3>Violacoes Recentes</h3>' + recent.map(v => `
                <div class="violation-item">
                    <span class="violation-severity ${v.severity.toLowerCase()}">[${v.severity}]</span>
                    ${esc(v.description)}
                    <div class="text-muted" style="font-size:11px;margin-top:4px;">
                        ${esc(v.command)} &mdash; ${v.timestamp}
                    </div>
                </div>
            `).join('');
        } else {
            list.innerHTML = '<h3>Violacoes Recentes</h3><p class="text-muted">Nenhuma violacao detectada. Sistema seguro.</p>';
        }
    } catch (e) {
        console.error('Erro ao carregar seguranca:', e);
    }
}

async function validateCommand() {
    const input = document.getElementById('validateInput');
    const command = input.value.trim();
    if (!command) return;

    const res = await fetch(`${API}/api/security/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command }),
    });
    const data = await res.json();
    const result = document.getElementById('validateResult');

    if (data.is_safe) {
        result.className = 'validate-result safe';
        result.innerHTML = `<strong>SEGURO</strong> &mdash; Comando permitido: <code>${esc(command)}</code>`;
    } else {
        const v = data.violation;
        result.className = 'validate-result blocked';
        result.innerHTML = `
            <strong>BLOQUEADO</strong> [${v.severity}]<br>
            <strong>${esc(v.description)}</strong><br>
            <span style="font-size:12px;">Padrao: <code>${esc(v.pattern)}</code></span>
        `;
    }

    refreshSecurity();
}

// === Clients ===
async function refreshClients() {
    try {
        const res = await fetch(`${API}/api/clients`);
        const data = await res.json();
        const grid = document.getElementById('clientGrid');

        grid.innerHTML = data.clients.map(c => `
            <div class="client-card">
                <h3>${esc(c.name)}</h3>
                <div class="client-path">${esc(c.config_path || 'N/A')}</div>
                <div class="client-status">
                    Config: ${c.exists
                        ? '<span style="color:var(--success)">Encontrado</span>'
                        : '<span style="color:var(--text-muted)">Nao encontrado</span>'
                    }
                </div>
                <button class="btn btn-primary btn-sm" onclick="configureClient('${esc(c.name)}')">
                    Exportar Servidores
                </button>
            </div>
        `).join('');
    } catch (e) {
        console.error('Erro ao carregar clientes:', e);
    }
}

async function configureClient(client) {
    const res = await fetch(`${API}/api/clients/${encodeURIComponent(client)}/configure`, { method: 'POST' });
    const data = await res.json();
    toast(data.success ? 'success' : 'error', data.message || data.error);
}

// === Logs ===
async function populateLogSelect() {
    const res = await fetch(`${API}/api/servers`);
    const data = await res.json();
    const select = document.getElementById('logServerSelect');
    const current = select.value;

    select.innerHTML = '<option value="">Selecione um servidor</option>';
    data.servers.forEach(s => {
        const opt = document.createElement('option');
        opt.value = s.name;
        opt.textContent = s.name;
        select.appendChild(opt);
    });

    if (current) select.value = current;
}

async function loadLogs() {
    const name = document.getElementById('logServerSelect').value;
    const viewer = document.getElementById('logViewer');

    if (!name) {
        viewer.textContent = 'Selecione um servidor para ver os logs.';
        return;
    }

    try {
        const res = await fetch(`${API}/api/servers/${encodeURIComponent(name)}/logs?lines=200`);
        const data = await res.json();
        viewer.textContent = data.logs || `Nenhum log para "${name}".`;
        viewer.scrollTop = viewer.scrollHeight;
    } catch (e) {
        viewer.textContent = 'Erro ao carregar logs.';
    }
}

// === Toasts ===
function toast(type, message) {
    const container = document.getElementById('toastContainer');
    const el = document.createElement('div');
    el.className = `toast toast-${type}`;
    el.textContent = message;
    container.appendChild(el);
    setTimeout(() => el.remove(), 4000);
}

// === Utils ===
function esc(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
