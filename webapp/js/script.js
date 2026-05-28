// Local Database State Initialization 
if (!localStorage.getItem('sid_initialized')) {
    localStorage.setItem('sid_bots', JSON.stringify([]));
    localStorage.setItem('sid_wallet', '0.00');
    localStorage.setItem('sid_premium', 'false');
    localStorage.setItem('sid_initialized', 'true');
}

function updateStoredBots(bots) {
    localStorage.setItem('sid_bots', JSON.stringify(bots));
    renderBotDashboard();
}

function calculateUptime(startTime) {
    if (!startTime) return '0m';
    const diffMins = Math.floor((Date.now() - startTime) / 60000);
    const diffHours = Math.floor(diffMins / 60);
    return diffHours > 0 ? `${diffHours}h ${diffMins % 60}m` : `${diffMins}m`;
}

// Layout Switch Tab Controllers
const nav = {
    switchTab: function(tabId, element) {
        document.querySelectorAll('.view-section').forEach(s => s.classList.add('hidden'));
        const target = document.getElementById(tabId);
        if (target) target.classList.remove('hidden');

        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        if (element) element.classList.add('active');

        if (tabId === 'view-files') renderBotDashboard();
        if (tabId === 'view-settings') appSettings.loadDashboard();
    }
};

// Orchestrated Script Upload and Multi-Step Verification Flow
const deployFlow = {
    tempData: { phone: '', script: '', fileName: 'main.py', apiId: '', apiHash: '' },

    handleFileUpload: function(event) {
        const file = event.target.files[0];
        if (file) {
            this.tempData.fileName = file.name;
            document.getElementById('targetFileNameDisplay').value = file.name;
            
            const reader = new FileReader();
            reader.onload = (e) => {
                const scriptText = e.target.result;
                document.getElementById('scriptInput').value = scriptText;
                this.extractLocalCredentials(scriptText);
            };
            reader.readAsText(file);
        }
    },

    extractLocalCredentials: function(text) {
        // Automatically check script environment configuration for embedded access pairs
        const idMatch = text.match(/(?:API_ID)\s*=\s*['"]?(\d+)['"]?/i);
        const hashMatch = text.match(/(?:API_HASH)\s*=\s*['"]?([a-fA-F0-9]{32})['"]/i);
        if (idMatch) this.tempData.apiId = idMatch[1];
        if (hashMatch) this.tempData.apiHash = hashMatch[1];
    },

    nextToOTP: function() {
        this.tempData.fileName = document.getElementById('targetFileNameDisplay').value.trim() || 'main.py';
        this.tempData.script = document.getElementById('scriptInput').value.trim();
        this.tempData.phone = document.getElementById('phoneInput').value.trim();

        if (!this.tempData.script) {
            alert('❌ Verification Error: Source script text environment cannot be blank.');
            return;
        }
        if (!this.tempData.phone) {
            alert('❌ Route Error: A routing phone node assignment identifier context is required.');
            return;
        }

        // Parse verification text for internal configurations dynamically if changed inside editing pane
        this.extractLocalCredentials(this.tempData.script);

        document.getElementById('step1-script').classList.add('hidden');
        document.getElementById('step2-otp').classList.remove('hidden');
    },

    nextToPassword: function() {
        const otpToken = document.getElementById('otpInput').value.trim();
        if (!otpToken) {
            alert('❌ Security Warning: Verification credential packet payload cannot be blank.');
            return;
        }
        document.getElementById('step2-otp').classList.add('hidden');
        document.getElementById('step3-password').classList.remove('hidden');
    },

    finalize: async function() {
        const btn = document.getElementById('btn-pass');
        const passwordVal = document.getElementById('passwordInput').value.trim();
        const otpToken = document.getElementById('otpInput').value.trim();
        
        btn.disabled = true;

        try {
            // Deliver complete system deployment profiles directly to server API backend
            const response = await fetch('/api/deploy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    fileName: this.tempData.fileName,
                    scriptSource: this.tempData.script,
                    phone: this.tempData.phone,
                    otp: otpToken,
                    password: passwordVal,
                    apiId: this.tempData.apiId,
                    apiHash: this.tempData.apiHash
                })
            });
            
            const result = await response.json();
            if (!response.ok) throw new Error(result.error || 'Server rejected container bundle setup.');

            const currentBots = JSON.parse(localStorage.getItem('sid_bots') || '[]');
            const newBotId = 'bot_' + Date.now();
            
            currentBots.push({
                id: newBotId,
                name: this.tempData.fileName,
                status: 'Stopped',
                uptime: '0m',
                ram: '0MB',
                startTime: null,
                traits: { type: 'Live Telethon Userbot Task' }
            });
            
            updateStoredBots(currentBots);

            document.getElementById('step3-password').classList.add('hidden');
            document.getElementById('step4-success').classList.remove('hidden');

            // Fire activation pipeline initialization block
            setTimeout(() => { this.triggerEngineStart(newBotId, this.tempData.fileName); }, 800);
        } catch (err) {
            alert(`❌ Compilation Pipeline Halted: ${err.message}`);
        } finally {
            btn.disabled = false;
        }
    },

    triggerEngineStart: async function(botId, fileName) {
        await fetch('/api/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ botId, fileName })
        });
        toggleBotStateInUI(botId, 'Running', Date.now());
    },

    goBack: function(from, to) {
        document.getElementById(from).classList.add('hidden');
        document.getElementById(to).classList.remove('hidden');
    },

    reset: function() {
        document.getElementById('scriptInput').value = '';
        document.getElementById('phoneInput').value = '';
        document.getElementById('otpInput').value = '';
        document.getElementById('passwordInput').value = '';
        document.getElementById('step4-success').classList.add('hidden');
        document.getElementById('step1-script').classList.remove('hidden');
    }
};

function toggleBotStateInUI(botId, status, startTime) {
    let bots = JSON.parse(localStorage.getItem('sid_bots') || '[]');
    bots = bots.map(b => {
        if (b.id === botId) {
            b.status = status;
            b.startTime = startTime;
            b.ram = status === 'Running' ? '18MB' : '0MB';
        }
        return b;
    });
    updateStoredBots(bots);
}

async function toggleBotState(botId) {
    const bots = JSON.parse(localStorage.getItem('sid_bots') || '[]');
    const target = bots.find(b => b.id === botId);
    if (!target) return;

    if (target.status !== 'Running') {
        const res = await fetch('/api/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ botId, fileName: target.name })
        });
        if (res.ok) toggleBotStateInUI(botId, 'Running', Date.now());
    } else {
        await fetch('/api/stop', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ botId })
        });
        toggleBotStateInUI(botId, 'Stopped', null);
    }
}

async function deleteBotAsset(botId) {
    const bots = JSON.parse(localStorage.getItem('sid_bots') || '[]');
    const target = bots.find(b => b.id === botId);
    if (!target) return;

    if (target.status === 'Running') {
        await fetch('/api/stop', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ botId })
        });
    }
    updateStoredBots(bots.filter(b => b.id !== botId));
}

function renderBotDashboard() {
    const bots = JSON.parse(localStorage.getItem('sid_bots') || '[]');
    const container = document.getElementById('bots-list-container');
    const counter = document.getElementById('bot-running-counter');
    if (!container) return;

    const updatedBots = bots.map(b => {
        if (b.status === 'Running' && b.startTime) b.uptime = calculateUptime(b.startTime);
        return b;
    });

    if (counter) {
        counter.innerText = `🟢 ${updatedBots.filter(b => b.status === 'Running').length} / ${updatedBots.length} Deployed Threads Active`;
    }

    container.innerHTML = updatedBots.length === 0 
        ? `<p style="text-align:center; color:var(--text-muted); padding:24px;">No script templates registered to local machine engine storage node.</p>`
        : '';

    updatedBots.forEach(bot => {
        const isRunning = bot.status === 'Running';
        const div = document.createElement('div');
        div.className = 'file-item';
        div.innerHTML = `
            <div>
                <div class="file-name">${bot.name} <span style="font-size:11px; color:var(--text-muted); font-weight:normal;">(${bot.traits.type})</span></div>
                <div class="file-status">${bot.status} • Runtime: ${isRunning ? bot.uptime : '0m'} • Compute: ${bot.ram}</div>
            </div>
            <div>
                <button class="action-btn" onclick="terminal.open('${bot.id}')">📝 Logs</button>
                <button class="action-btn" onclick="toggleBotState('${bot.id}')" style="color: ${isRunning ? '#ffd700' : '#34d399'}">${isRunning ? '🔄 Restart' : '▶ Start'}</button>
                <button class="action-btn danger" onclick="deleteBotAsset('${bot.id}')">${isRunning ? '⏹ Stop' : '🗑 Delete'}</button>
            </div>
        `;
        container.appendChild(div);
    });
}

let logInterval = null;
const terminal = {
    open: function(botId) {
        if (logInterval) clearInterval(logInterval);
        const modal = document.getElementById('terminal-modal');
        modal.classList.remove('hidden');

        logInterval = setInterval(async () => {
            try {
                const res = await fetch(`/api/logs/${botId}`);
                const data = await res.json();
                document.getElementById('terminal-output').innerHTML = data.logs.map(l => `<div class="log-line">${l}</div>`).join('');
                document.getElementById('terminal-output').scrollTop = document.getElementById('terminal-output').scrollHeight;
            } catch (e) {
                document.getElementById('terminal-output').innerHTML = `<div class="log-line" style="color:var(--color-danger)">[ERR] Server streaming interface connection drops detected.</div>`;
            }
        }, 1000);
    },
    close: function() {
        document.getElementById('terminal-modal').classList.add('hidden');
        if (logInterval) clearInterval(logInterval);
        renderBotDashboard();
    }
};

const appSettings = {
    loadDashboard: function() {
        const premium = localStorage.getItem('sid_premium') === 'true';
        document.getElementById('settings-account-status').innerText = premium ? '💎 Premium Cluster Pro Member' : 'Standard Node Edition';
        document.getElementById('settings-wallet-balance').innerText = `$${localStorage.getItem('sid_wallet') || '0.00'}`;
    },
    purchasePremium: function() {
        localStorage.setItem('sid_premium', 'true');
        localStorage.setItem('sid_wallet', '150.00');
        this.loadDashboard();
    }
};

document.addEventListener('DOMContentLoaded', () => { renderBotDashboard(); });
