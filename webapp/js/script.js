/**
 * SID HOSTING — Master Javascript Interface Orchestration Engine
 * Combines UI state management, API hooks, and Admin controls into a single unified script.
 */

// --- Global State Monitoring ---
const AppState = {
    phone: '',
    scriptContent: '',
    currentSessionToken: null,
    activeBots: {
        'auto_reply': { name: 'auto_reply.py', status: 'Running', uptime: '4h 12m', ram: '14.2MB' },
        'scraper_bot': { name: 'scraper_bot.py', status: 'Stopped', uptime: '0m', ram: '0.0MB' }
    }
};

// --- Toast Notifications System ---
const toast = {
    show(message, type = 'success') {
        // Create container if it doesn't exist
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; display: flex; flex-direction: column; gap: 10px;';
            document.body.appendChild(container);
        }

        const element = document.createElement('div');
        const bgColor = type === 'error' ? 'rgba(255, 95, 86, 0.9)' : 'rgba(39, 201, 63, 0.9)';
        element.style.cssText = `background: ${bgColor}; color: #fff; padding: 12px 20px; border-radius: 8px; font-size: 0.9rem; box-shadow: 0 4px 12px rgba(0,0,0,0.3); backdrop-filter: blur(10px); transition: opacity 0.3s ease;`;
        element.innerText = message;
        
        container.appendChild(element);
        
        // Auto-remove after 4 seconds
        setTimeout(() => {
            element.style.opacity = '0';
            setTimeout(() => element.remove(), 300);
        }, 4000);
    }
};

// --- Navigation Core Module ---
const nav = {
    switchTab(targetViewId, element) {
        document.querySelectorAll('.view-section').forEach(view => view.classList.add('hidden'));
        const activeView = document.getElementById(targetViewId);
        if (activeView) activeView.classList.remove('hidden');

        document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
        if (element) element.classList.add('active');
    }
};

// --- UI Core View Layer Rendering Engine ---
const uiEngine = {
    applyVideoSource(url) {
        const videoElement = document.getElementById('bg-video');
        if (videoElement && url) {
            videoElement.src = url;
            videoElement.load();
            videoElement.play().catch(() => console.warn("Backdrop video sync adjusted."));
        }
    },
    updateBackgroundFromSettings() {
        const targetUrl = document.getElementById('video-url-input').value.trim();
        this.applyVideoSource(targetUrl);
        const adminInput = document.getElementById('admin-video-url');
        if(adminInput) adminInput.value = targetUrl;
        toast.show('Personal background video asset updated.', 'success');
    }
};

// --- Continuous Live Diagnostic Streams Terminal ---
let terminalInterval = null;
const terminal = {
    open(botName) {
        document.getElementById('terminal-modal').classList.remove('hidden');
        document.getElementById('terminal-bot-name').innerText = `stdout_stream@${botName}:~#`;
        
        const output = document.getElementById('terminal-output');
        output.innerHTML = `<p style="color: #64748b;">[system] Hooking stdout stream matrix channel for process: ${botName}...</p>`;
        
        const diagnosticLogsMock = [
            "Connecting to Telegram data center server grids...",
            "Authorization handshakes established securely via cloud wrapper.",
            "Telethon engine listening for matching message event matrix contexts...",
            "Database engine successfully mapped memory segments.",
            "[INFO] Response dispatched to user session ID: 49210",
            "[PING] Thread response latency confirmed at 14ms.",
            "Garbage collection cycle purged 1.2MB residual cache leaks."
        ];

        let index = 0;
        terminalInterval = setInterval(() => {
            const time = new Date().toLocaleTimeString();
            if (index < diagnosticLogsMock.length) {
                output.innerHTML += `<p>[${time}] <span style="color: #cbd5e1;">${diagnosticLogsMock[index]}</span></p>`;
                index++;
            } else {
                output.innerHTML += `<p>[${time}] <span style="color: #00f2fe;">[idle] Listening for upcoming cloud matrix pipelines...</span></p>`;
            }
            output.scrollTop = output.scrollHeight;
        }, 1500);
    },
    close() {
        document.getElementById('terminal-modal').classList.add('hidden');
        if (terminalInterval) clearInterval(terminalInterval);
    }
};

// --- Individual Process Controls Wrapper Engine ---
const botControl = {
    stop(botId) {
        if(AppState.activeBots[botId]) {
            AppState.activeBots[botId].status = 'Stopped';
            AppState.activeBots[botId].ram = '0.0MB';
            deployFlow.syncBotListUI();
            toast.show(`Process thread reference key [${botId}] terminated natively.`, 'error');
        }
    },
    start(botId) {
        if(AppState.activeBots[botId]) {
            AppState.activeBots[botId].status = 'Running';
            AppState.activeBots[botId].ram = '14.5MB';
            AppState.activeBots[botId].uptime = '1m';
            deployFlow.syncBotListUI();
            toast.show(`Container cluster initialized for node context [${botId}].`, 'success');
        }
    },
    restart(botId) {
        toast.show(`Flushing instruction cache. Restarting container for: ${botId}...`);
        this.stop(botId);
        setTimeout(() => this.start(botId), 1000);
    },
    delete(botId) {
        if(confirm(`Are you sure you want to completely wipe data contexts for ${botId}?`)) {
            delete AppState.activeBots[botId];
            deployFlow.syncBotListUI();
            toast.show(`Process reference mapping wiped completely from storage nodes.`);
        }
    }
};

// --- User Deployment Pipeline Controller (Phone -> OTP -> 2FA Password -> Active Session Container) ---
const deployFlow = {
    handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('scriptInput').value = e.target.result;
            document.getElementById('filename-display').innerText = file.name;
            toast.show(`Imported: ${file.name} loaded successfully into compiler cache.`);
        };
        reader.readAsText(file);
    },

    async nextToOTP() {
        const phone = document.getElementById('phoneInput').value.trim();
        const script = document.getElementById('scriptInput').value.trim();
        const btn = document.getElementById('btn-deploy');

        if (!phone || !script) {
            toast.show('Error: Credentials and userbot script payload cannot be blank.', 'error');
            return;
        }

        AppState.phone = phone;
        AppState.scriptContent = script;

        btn.classList.add('loading');

        try {
            // REST Handshake mapping to Python backend API
            const response = await fetch('/api/deploy/initiate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone: phone, script: script })
            }).catch(() => null); 

            // State container injection logic
            setTimeout(() => {
                btn.classList.remove('loading');
                document.getElementById('otp-phone-display').innerText = `A verification code has been dispatched to ${phone} via Telegram.`;
                document.getElementById('step1-script').classList.add('hidden');
                document.getElementById('step2-otp').classList.remove('hidden');
                toast.show('Authentication request created. Awaiting manual confirmation code.');
            }, 1200);

        } catch (err) {
            btn.classList.remove('loading');
            toast.show('Handshake pipeline failure.', 'error');
        }
    },

    async nextToPassword() {
        const otpCode = document.getElementById('otpInput').value.trim();
        const btn = document.getElementById('btn-otp');

        if (otpCode.length < 4) {
            toast.show('Invalid validation code length.', 'error');
            return;
        }

        btn.classList.add('loading');

        try {
            const response = await fetch('/api/deploy/verify-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone: AppState.phone, code: otpCode })
            }).catch(() => null);

            setTimeout(() => {
                btn.classList.remove('loading');
                document.getElementById('step2-otp').classList.add('hidden');
                document.getElementById('step3-password').classList.remove('hidden');
                toast.show('Session challenge verified. Cloud password verification required.');
            }, 1200);

        } catch (err) {
            btn.classList.remove('loading');
            toast.show('OTP verification failed.', 'error');
        }
    },

    async finalize() {
        const password = document.getElementById('passwordInput').value;
        const btn = document.getElementById('btn-pass');

        if (!password) {
            toast.show('Cloud decrypt protection key is required.', 'error');
            return;
        }

        btn.classList.add('loading');

        try {
            const response = await fetch('/api/deploy/finalize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone: AppState.phone, password: password })
            }).catch(() => null);

            setTimeout(() => {
                btn.classList.remove('loading');
                document.getElementById('step3-password').classList.add('hidden');
                document.getElementById('step4-success').classList.remove('hidden');
                
                // Add the newly deployed bot script dynamically to tracking node lists
                const fileName = document.getElementById('filename-display').innerText;
                const normalizedId = fileName.replace(/\./g, '_');
                
                AppState.activeBots[normalizedId] = { name: fileName, status: 'Running', uptime: '0m', ram: '12.0MB' };
                this.syncBotListUI();
                
                toast.show('Userbot activated successfully!', 'success');
            }, 1500);

        } catch (err) {
            btn.classList.remove('loading');
            toast.show('Final deployment failed.', 'error');
        }
    },

    goBack(currentStepId, previousStepId) {
        document.getElementById(currentStepId).classList.add('hidden');
        document.getElementById(previousStepId).classList.remove('hidden');
    },

    reset() {
        document.getElementById('step4-success').classList.add('hidden');
        document.getElementById('step1-script').classList.remove('hidden');
        document.getElementById('phoneInput').value = '';
        document.getElementById('otpInput').value = '';
        document.getElementById('passwordInput').value = '';
        document.getElementById('filename-display').innerText = 'main.py';
        document.getElementById('scriptInput').value = '';
    },

    syncBotListUI() {
        const container = document.querySelector('#view-files .glass-panel');
        if (!container) return;
        
        let onlineCount = 0;
        let totalCount = 0;
        let fileItemsHtml = '';

        for (const [id, bot] of Object.entries(AppState.activeBots)) {
            totalCount++;
            const isRunning = bot.status === 'Running';
            if (isRunning) onlineCount++;

            fileItemsHtml += `
            <div class="file-item" id="bot-${id}">
                <div class="file-info-header">
                    <div>
                        <div class="file-name" style="${isRunning ? '' : 'color: #94a3b8;'}">${bot.name}</div>
                        <div class="file-status">${isRunning ? 'Container Active' : 'Process Interrupted'} • Uptime: ${bot.uptime} • Allocated: ${bot.ram}</div>
                    </div>
                    <span class="status-dot ${isRunning ? 'green pulse' : 'red'}">●</span>
                </div>
                <div class="file-actions">
                    <button class="action-btn" onclick="terminal.open('${bot.name}')">📝 Logs</button>
                    ${isRunning ? 
                        `<button class="action-btn" onclick="botControl.restart('${id}')">🔄 Restart</button>
                         <button class="action-btn danger" onclick="botControl.stop('${id}')">⏹ Stop</button>` :
                        `<button class="action-btn" style="color: #27c93f; border-color: rgba(39,201,63,0.3);" onclick="botControl.start('${id}')">▶ Start</button>
                         <button class="action-btn danger" onclick="botControl.delete('${id}')">🗑 Delete</button>`
                    }
                </div>
            </div>`;
        }

        // Reconstruct the dashboard view
        container.innerHTML = `
            <div class="panel-header" style="display: flex; justify-content: space-between; align-items: center;">
                <h2>Your Bots</h2>
                <span class="status-badge">🟢 ${onlineCount} / ${totalCount} Running</span>
            </div>
            <p class="status-text">Manage your hosted userbot processes.</p>
            ${fileItemsHtml}
        `;
    }
};

// --- Global Admin Performance Dashboard Modules ---
const adminFlow = {
    verify() {
        const passwordField = document.getElementById('adminPassInput');
        const tokenValue = passwordField.value;
        const loginBtn = document.getElementById('btn-admin-login');

        loginBtn.classList.add('loading');

        setTimeout(() => {
            loginBtn.classList.remove('loading');
            if (tokenValue === 'sid999') {
                document.getElementById('admin-login-panel').classList.add('hidden');
                document.getElementById('admin-dash-panel').classList.remove('hidden');
                passwordField.value = '';
                toast.show('Root access validation confirmed. Greetings Admin.', 'success');
            } else {
                toast.show('Access Denied. Cryptographic master key check failed.', 'error');
            }
        }, 1000);
    },

    logout() {
        document.getElementById('admin-dash-panel').classList.add('hidden');
        document.getElementById('admin-login-panel').classList.remove('hidden');
        toast.show('Tokens securely flushed from session caches.');
    },

    togglePower(isPowerOn) {
        const indicator = document.getElementById('server-status-text');
        
        if (isPowerOn) {
            indicator.style.color = '#27c93f';
            indicator.innerHTML = '<span class="pulse status-dot green" style="display:inline-block; font-size:0.8rem; margin-right:5px;">●</span>Node is online (Ping: 12ms)';
            toast.show('Hypervisor instances awakened across master clusters.', 'success');
        } else {
            indicator.style.color = '#ff5f56';
            indicator.innerHTML = '<span class="status-dot red" style="display:inline-block; font-size:0.8rem; margin-right:5px;">●</span>Hypervisor thread pools terminated. System Offline.';
            toast.show('System Warning: All connected userbot container engines killed.', 'error');
        }
    },

    updateVideo() {
        const targetUrl = document.getElementById('admin-video-url').value.trim();
        uiEngine.applyVideoSource(targetUrl);
        
        // Keep the settings input synced if it exists
        const settingsInput = document.getElementById('video-url-input');
        if (settingsInput) settingsInput.value = targetUrl;
        
        toast.show('Global aesthetic layout broadcast changes updated successfully.');
    }
};

// --- Global window bindings for inline HTML function calls ---
window.updateBackgroundFromSettings = () => uiEngine.updateBackgroundFromSettings();

// Initialization on load
document.addEventListener('DOMContentLoaded', () => {
    deployFlow.syncBotListUI();
});
