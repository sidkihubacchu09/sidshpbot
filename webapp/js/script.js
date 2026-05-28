/**
 * SID HOSTING — Master Javascript Interface Orchestration Engine
 */

// Global state monitoring
const AppState = {
    phone: '',
    scriptContent: '',
    currentSessionToken: null,
    activeBots: {
        'auto_reply': { name: 'auto_reply.py', status: 'Running', uptime: '4h 12m', ram: '14.2MB' },
        'scraper_bot': { name: 'scraper_bot.py', status: 'Stopped', uptime: '0m', ram: '0.0MB' }
    }
};

// Toast Notifications System
const toast = {
    show(message, type = 'success') {
        const container = document.getElementById('toast-container');
        const element = document.createElement('div');
        element.className = `toast ${type}`;
        element.innerText = message;
        container.appendChild(element);
        setTimeout(() => { element.remove(); }, 4000);
    }
};

// Navigation Core Module
const nav = {
    switchTab(targetViewId, element) {
        document.querySelectorAll('.view-section').forEach(view => view.classList.add('hidden'));
        const activeView = document.getElementById(targetViewId);
        if (activeView) activeView.classList.remove('hidden');

        document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
        if (element) element.classList.add('active');
    }
};

// User Deployment Pipeline Controller (Phone -> OTP -> 2FA Password -> Active Session Container)
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

        // Toggle micro-processing state
        btn.classList.add('loading');

        try {
            // REST Handshake mapping to Python backend API
            const response = await fetch('/api/deploy/initiate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone: phone, script: script })
            }).catch(() => null); // Fallback if server is not fully initialized

            // Simulated state container injection logic for frontend demonstration
            setTimeout(() => {
                btn.classList.remove('loading');
                document.getElementById('otp-phone-display').innerText = `A 5-digit verification code has been dispatched to ${phone} via Telegram.`;
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
                body: JSON.stringify({ code: otpCode })
            }).catch(() => null);

            setTimeout(() => {
                btn.classList.remove('loading');
                // Backend signal emulation determining if 2FA cloud password challenge is active
                document.getElementById('step2-otp').classList.add('hidden');
                document.getElementById('step3-password').classList.remove('hidden');
                toast.show('Session challenge verified. Cloud password verification required.');
            }, 1200);

        } catch (err) {
            btn.classList.remove('loading');
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
                body: JSON.stringify({ password: password })
            }).catch(() => null);

            setTimeout(() => {
                btn.classList.remove('loading');
                document.getElementById('step3-password').classList.add('hidden');
                document.getElementById('step4-success').classList.remove('hidden');
                
                // Add the newly deployed bot script dynamically to our visible tracking node lists
                const fileName = document.getElementById('filename-display').innerText;
                const normalizedId = fileName.replace('.', '_');
                
                AppState.activeBots[normalizedId] = { name: fileName, status: 'Running', uptime: '0m', ram: '12.0MB' };
                this.syncBotListUI();
                
                toast.show('Userbot activated successfully!', 'success');
            }, 1500);

        } catch (err) {
            btn.classList.remove('loading');
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
        document.getElementById('filename-display').innerText = 'userbot_main.py';
        document.getElementById('scriptInput').value = '';
    },

    syncBotListUI() {
        const container = document.getElementById('bots-list-container');
        if (!container) return;
        
        let html = '';
        let onlineCount = 0;
        let totalCount = 0;

        for (const [id, bot] of Object.entries(AppState.activeBots)) {
            totalCount++;
            const isRunning = bot.status === 'Running';
            if (isRunning) onlineCount++;

            html += `
            <div class="file-item ${isRunning ? '' : 'process-stopped'}" id="bot-${id}">
                <div class="file-info-header">
                    <div>
                        <div class="file-name ${isRunning ? '' : 'text-muted-name'}">${bot.name}</div>
                        <div class="file-status">${isRunning ? 'Container Active' : 'Process Interrupted'} • Uptime: <span class="timer">${bot.uptime}</span> • Allocated: ${bot.ram}</div>
                    </div>
                    <span class="status-dot ${isRunning ? 'green pulse' : 'red'}">●</span>
                </div>
                <div class="file-actions">
                    <button class="action-btn text-transparent-glow" onclick="terminal.open('${bot.name}')">📝 Terminal Logs</button>
                    ${isRunning ? 
                        `<button class="action-btn text-transparent-glow" onclick="botControl.restart('${id}')">🔄 Restart Thread</button>
                         <button class="action-btn danger text-transparent-glow" onclick="botControl.stop('${id}')">⏹ Terminate</button>` :
                        `<button class="action-btn success-btn text-transparent-glow" onclick="botControl.start('${id}')">▶ Initialize Node</button>
                         <button class="action-btn danger text-transparent-glow" onclick="botControl.delete('${id}')">🗑 Wipe Storage</button>`
                    }
                </div>
            </div>`;
        }
        container.innerHTML = html;
        document.getElementById('bot-count-badge').innerText = `🟢 ${onlineCount} / ${totalCount} Threads Online`;
    }
};

// Individual Process Controls Wrapper Engine
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

// Continuous Live Diagnostic Streams Terminal
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
                output.innerHTML += `<p>[${time}] <span style="color: var(--accent-cyber);">[idle] Listening for upcoming cloud matrix pipelines...</span></p>`;
            }
            output.scrollTop = output.scrollHeight;
        }, 1500);
    },
    close() {
        document.getElementById('terminal-modal').classList.add('hidden');
        if (terminalInterval) clearInterval(terminalInterval);
    }
};

// Global Admin Performance Dashboard Modules
const adminDashboard = {
    verifyPassword() {
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
                toast.show('Root access validation confirmed. Greetings Admin Sid.', 'success');
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

    toggleServerPower(isPowerOn) {
        const indicator = document.getElementById('server-status-text');
        const globalBadge = document.getElementById('global-server-badge');
        
        if (isPowerOn) {
            indicator.style.color = 'var(--sys-green)';
            indicator.innerHTML = '<span class="pulse status-dot green">●</span>Primary Node Cluster operational (Cluster Latency: 12ms)';
            globalBadge.className = "badge active-badge";
            globalBadge.innerText = "● Engine Online";
            toast.show('Hypervisor instances awakened across master clusters.', 'success');
        } else {
            indicator.style.color = 'var(--sys-red)';
            indicator.innerHTML = '<span class="status-dot red">●</span>Hypervisor thread pools terminated. System Offline.';
            globalBadge.className = "badge premium-badge";
            globalBadge.innerText = "⏹ Engine Dead";
            toast.show('System Warning: All connected userbot container engines killed.', 'error');
        }
    },

    updateGlobalBackground() {
        const targetUrl = document.getElementById('admin-video-url-input').value.trim();
        uiEngine.applyVideoSource(targetUrl);
        document.getElementById('video-url-input').value = targetUrl;
        toast.show('Global aesthetic layout broadcast changes updated successfully.');
    }
};

// UI Core View Layer Rendering Engine
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
        document.getElementById('admin-video-url-input').value = targetUrl;
        toast.show('Personal background video asset updated.', 'success');
    }
};
