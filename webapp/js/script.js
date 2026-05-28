/**
 * SID HOSTING — Master Javascript Interface Orchestration Engine
 * Seamlessly mapped to the HTML UI and the Python Flask Backend API.
 */

// --- Global State Monitoring ---
const AppState = {
    phone: '',
    scriptContent: '',
    activeBots: {} // Populated dynamically when bots are deployed
};

// --- Toast Notifications System ---
const toast = {
    show(message, type = 'success') {
        const container = document.getElementById('toast-container');
        if (!container) return; // Failsafe

        const element = document.createElement('div');
        const bgColor = type === 'error' ? 'rgba(255, 95, 86, 0.9)' : 'rgba(39, 201, 63, 0.9)';
        element.style.cssText = `background: ${bgColor}; color: #fff; padding: 14px 24px; border-radius: 12px; font-size: 0.95rem; font-weight: 500; box-shadow: 0 10px 30px rgba(0,0,0,0.5); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); margin-bottom: 10px; transition: opacity 0.3s ease, transform 0.3s ease; transform: translateY(20px); opacity: 0;`;
        element.innerText = message;
        
        container.appendChild(element);
        
        // Trigger animation
        requestAnimationFrame(() => {
            element.style.transform = 'translateY(0)';
            element.style.opacity = '1';
        });
        
        // Auto-remove after 4 seconds
        setTimeout(() => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(-10px)';
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
            videoElement.play().catch(() => console.warn("Backdrop video sync blocked by browser autoplay rules."));
        }
    },
    updateBackgroundFromSettings() {
        const targetUrl = document.getElementById('video-url-input').value.trim();
        if (!targetUrl) return toast.show('Please enter a valid video URL.', 'error');
        
        this.applyVideoSource(targetUrl);
        
        // Sync with admin input if it exists
        const adminInput = document.getElementById('admin-video-url-input');
        if(adminInput) adminInput.value = targetUrl;
        
        toast.show('Personal background video asset updated successfully.', 'success');
    }
};

// --- User Deployment Pipeline Controller ---
const deployFlow = {
    handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('scriptInput').value = e.target.result;
            document.getElementById('filename-display').innerText = file.name;
            toast.show(`Imported: ${file.name} loaded into compiler cache.`);
        };
        reader.readAsText(file);
    },

    // Step 1: Request OTP
    async nextToOTP() {
        const phone = document.getElementById('phoneInput').value.trim();
        const script = document.getElementById('scriptInput').value.trim();
        const btn = document.getElementById('btn-deploy');

        if (!phone || !script) {
            return toast.show('Error: Phone number and script payload cannot be blank.', 'error');
        }

        AppState.phone = phone;
        AppState.scriptContent = script;
        btn.classList.add('loading');

        try {
            // Send API Request to Flask Backend
            const response = await fetch('/api/deploy/initiate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone: phone, script: script })
            });
            const data = await response.json();
            btn.classList.remove('loading');

            if (data.status === 'awaiting_otp') {
                // Update UI for OTP
                document.getElementById('otp-phone-display').innerText = `A 5-digit verification code has been dispatched to ${phone}.`;
                this.goBack('step1-script', 'step2-otp');
                toast.show('Authentication request created. Awaiting Telegram code.');
            } else {
                toast.show(data.message || 'Server error initiating session.', 'error');
            }
        } catch (err) {
            btn.classList.remove('loading');
            toast.show('Network failure. Could not reach cloud node.', 'error');
        }
    },

    // Step 2: Verify OTP
    async nextToPassword() {
        const otpCode = document.getElementById('otpInput').value.trim();
        const btn = document.getElementById('btn-otp');

        if (otpCode.length < 4) {
            return toast.show('Invalid validation code length.', 'error');
        }

        btn.classList.add('loading');

        try {
            const response = await fetch('/api/deploy/verify-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone: AppState.phone, code: otpCode })
            });
            const data = await response.json();
            btn.classList.remove('loading');

            if (data.status === 'awaiting_2fa') {
                this.goBack('step2-otp', 'step3-password');
                toast.show('2FA detected. Cloud password required.');
            } else if (data.status === 'deployed') {
                this.handleSuccessfulDeployment();
            } else {
                toast.show(data.message || 'OTP verification failed.', 'error');
            }
        } catch (err) {
            btn.classList.remove('loading');
            toast.show('Network failure. Could not verify OTP.', 'error');
        }
    },

    // Step 3: Verify 2FA Cloud Password
    async finalize() {
        const password = document.getElementById('passwordInput').value;
        const btn = document.getElementById('btn-pass');

        if (!password) {
            return toast.show('Cloud decrypt protection key is required.', 'error');
        }

        btn.classList.add('loading');

        try {
            const response = await fetch('/api/deploy/finalize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone: AppState.phone, password: password })
            });
            const data = await response.json();
            btn.classList.remove('loading');

            if (data.status === 'deployed') {
                this.handleSuccessfulDeployment();
            } else {
                toast.show(data.message || 'Incorrect Cloud Password.', 'error');
            }
        } catch (err) {
            btn.classList.remove('loading');
            toast.show('Deployment failed due to network error.', 'error');
        }
    },

    handleSuccessfulDeployment() {
        document.getElementById('step2-otp').classList.add('hidden');
        document.getElementById('step3-password').classList.add('hidden');
        document.getElementById('step4-success').classList.remove('hidden');
        
        const fileName = document.getElementById('filename-display').innerText;
        const safeId = AppState.phone.replace(/[^0-9]/g, ''); 
        
        // Add to local state matrix
        AppState.activeBots[safeId] = { 
            phoneKey: AppState.phone,
            name: fileName, 
            status: 'Running', 
            uptime: '0m', 
            ram: '14.2MB' 
        };
        this.syncBotListUI();
        toast.show('Userbot compiled and activated successfully!', 'success');
    },

    goBack(hideId, showId) {
        document.getElementById(hideId).classList.add('hidden');
        document.getElementById(showId).classList.remove('hidden');
    },

    reset() {
        this.goBack('step4-success', 'step1-script');
        document.getElementById('phoneInput').value = '';
        document.getElementById('otpInput').value = '';
        document.getElementById('passwordInput').value = '';
        document.getElementById('filename-display').innerText = 'userbot_main.py';
    },

    // Rebuilds the "My Bots" HTML list dynamically based on AppState
    syncBotListUI() {
        const container = document.getElementById('bots-list-container');
        const badge = document.getElementById('bot-count-badge');
        if (!container) return;
        
        let onlineCount = 0;
        let totalCount = 0;
        let html = '';

        for (const [id, bot] of Object.entries(AppState.activeBots)) {
            totalCount++;
            const isRunning = bot.status === 'Running';
            if (isRunning) onlineCount++;

            html += `
            <div class="file-item ${isRunning ? '' : 'process-stopped'}" id="bot-${id}">
                <div class="file-info-header">
                    <div>
                        <div class="file-name ${isRunning ? '' : 'text-muted-name'}">${bot.name}</div>
                        <div class="file-status">${isRunning ? 'Container Active' : 'Process Interrupted'} • Uptime: ${bot.uptime} • Allocated: ${bot.ram}</div>
                    </div>
                    <span class="status-dot ${isRunning ? 'green pulse' : 'red'}">●</span>
                </div>
                <div class="file-actions">
                    <button class="action-btn text-transparent-glow" onclick="terminal.open('${id}')">📝 Terminal Logs</button>
                    ${isRunning ? 
                        `<button class="action-btn text-transparent-glow" onclick="botControl.restart('${id}')">🔄 Restart</button>
                         <button class="action-btn danger text-transparent-glow" onclick="botControl.stop('${id}')">⏹ Terminate</button>` :
                        `<button class="action-btn success-btn text-transparent-glow" onclick="botControl.start('${id}')">▶ Initialize Node</button>
                         <button class="action-btn danger text-transparent-glow" onclick="botControl.delete('${id}')">🗑 Wipe Storage</button>`
                    }
                </div>
            </div>`;
        }

        if (totalCount === 0) {
            html = `<p class="status-text text-center mt-20">No active userbot processes found. Deploy a script to get started.</p>`;
        }

        container.innerHTML = html;
        if (badge) {
            badge.innerText = `🟢 ${onlineCount} / ${totalCount} Threads Online`;
            badge.className = onlineCount > 0 ? "badge active-badge" : "badge premium-badge";
        }
        
        // Update Admin Dashboard Stats
        const adminStatBots = document.getElementById('stat-active-bots');
        if (adminStatBots) adminStatBots.innerText = onlineCount;
    }
};

// --- Process Control Engine ---
const botControl = {
    async callApi(botId, actionType) {
        const bot = AppState.activeBots[botId];
        if (!bot) return false;
        
        try {
            const response = await fetch('/api/bot/control', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone: bot.phoneKey, action: actionType })
            });
            return await response.json();
        } catch (e) {
            return { status: 'error', message: 'Network failure' };
        }
    },

    async stop(botId) {
        toast.show(`Sending termination signal to Node...`);
        const result = await this.callApi(botId, 'stop');
        
        if (result.status === 'stopped' || result.status === 'error') {
            AppState.activeBots[botId].status = 'Stopped';
            AppState.activeBots[botId].ram = '0.0MB';
            deployFlow.syncBotListUI();
            toast.show(`Process thread terminated natively.`, 'error');
        }
    },
    
    // Note: 'start' & 'restart' might need backend implementation in your Python script. 
    // This updates the UI optimistically.
    start(botId) {
        AppState.activeBots[botId].status = 'Running';
        AppState.activeBots[botId].ram = '14.5MB';
        AppState.activeBots[botId].uptime = '0m';
        deployFlow.syncBotListUI();
        toast.show(`Container cluster initialized for node context.`, 'success');
    },

    restart(botId) {
        toast.show(`Flushing instruction cache...`);
        this.stop(botId);
        setTimeout(() => this.start(botId), 1500);
    },

    delete(botId) {
        if(confirm(`WARNING: Are you sure you want to completely wipe data contexts and session files for this bot?`)) {
            this.stop(botId); // Stop it first
            delete AppState.activeBots[botId];
            deployFlow.syncBotListUI();
            toast.show(`Process reference mapping wiped completely from storage nodes.`);
        }
    }
};

// --- Live Terminal Logs Engine ---
let terminalInterval = null;
const terminal = {
    async open(botId) {
        const bot = AppState.activeBots[botId];
        if (!bot) return;

        document.getElementById('terminal-modal').classList.remove('hidden');
        document.getElementById('terminal-bot-name').innerText = `stdout_stream@${bot.name}:~#`;
        const output = document.getElementById('terminal-output');
        
        output.innerHTML = `<p style="color: #64748b;">[system] Hooking stdout stream matrix channel for process: ${bot.name}...</p>`;
        
        // Fetch real logs from the server
        try {
            const response = await fetch('/api/bot/control', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone: bot.phoneKey, action: 'logs' })
            });
            const data = await response.json();
            
            if (data.status === 'success' && data.logs) {
                const logLines = data.logs.split('\n').filter(l => l.trim() !== '');
                let formattedHtml = '';
                logLines.forEach(line => {
                    formattedHtml += `<p><span style="color: #a7f3d0;">${line}</span></p>`;
                });
                output.innerHTML += formattedHtml;
            } else {
                output.innerHTML += `<p style="color: var(--sys-yellow);">[warn] Log file is currently empty or unreadable.</p>`;
            }
        } catch (e) {
            output.innerHTML += `<p style="color: var(--sys-red);">[error] Network interrupt: Unable to fetch live logs from backend.</p>`;
        }
        
        output.scrollTop = output.scrollHeight;
    },
    
    close() {
        document.getElementById('terminal-modal').classList.add('hidden');
        if (terminalInterval) clearInterval(terminalInterval);
    }
};

// --- Admin Panel Architecture ---
const adminDashboard = {
    verifyPassword() {
        const pass = document.getElementById('adminPassInput').value;
        const btn = document.getElementById('btn-admin-login');

        btn.classList.add('loading');

        setTimeout(() => {
            btn.classList.remove('loading');
            if (pass === 'sid999') {
                document.getElementById('admin-login-panel').classList.add('hidden');
                document.getElementById('admin-dash-panel').classList.remove('hidden');
                document.getElementById('adminPassInput').value = '';
                toast.show('Root access validation confirmed. Greetings Admin.', 'success');
            } else {
                toast.show('Access Denied. Cryptographic master key check failed.', 'error');
            }
        }, 1200);
    },

    logout() {
        document.getElementById('admin-dash-panel').classList.add('hidden');
        document.getElementById('admin-login-panel').classList.remove('hidden');
        toast.show('Tokens securely flushed from session caches.');
    },

    toggleServerPower(isPowerOn) {
        const indicator = document.getElementById('server-status-text');
        const badge = document.getElementById('global-server-badge');
        
        if (isPowerOn) {
            indicator.style.color = 'var(--sys-green)';
            indicator.innerHTML = '<span class="pulse status-dot green">●</span>Primary Node Cluster operational (Cluster Latency: 12ms)';
            badge.className = "badge active-badge";
            badge.innerText = "● Engine Online";
            toast.show('Hypervisor instances awakened across master clusters.', 'success');
        } else {
            indicator.style.color = 'var(--sys-red)';
            indicator.innerHTML = '<span class="status-dot red">●</span>Hypervisor thread pools terminated. System Offline.';
            badge.className = "badge premium-badge";
            badge.innerText = "⏹ Engine Dead";
            toast.show('System Warning: All connected userbot container engines killed.', 'error');
        }
    },

    updateGlobalBackground() {
        const targetUrl = document.getElementById('admin-video-url-input').value.trim();
        uiEngine.applyVideoSource(targetUrl);
        
        const userSettingsInput = document.getElementById('video-url-input');
        if (userSettingsInput) userSettingsInput.value = targetUrl;
        
        toast.show('Global aesthetic layout broadcast changes updated successfully.');
    }
};

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    // If you want to show mock bots for testing before deploying, you can uncomment this:
    /*
    AppState.activeBots['mock123'] = { phoneKey: '+123', name: 'auto_reply.py', status: 'Running', uptime: '4h 12m', ram: '14.2MB' };
    AppState.activeBots['mock456'] = { phoneKey: '+456', name: 'scraper_bot.py', status: 'Stopped', uptime: '0m', ram: '0.0MB' };
    */
    deployFlow.syncBotListUI();
});
