const AppState = {
    phone: '',
    scriptContent: '',
    activeBots: {} 
};

const toast = {
    show(message, type = 'success') {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; display: flex; flex-direction: column; gap: 10px;';
            document.body.appendChild(container);
        }

        const element = document.createElement('div');
        const bgColor = type === 'error' ? 'rgba(255, 95, 86, 0.9)' : 'rgba(39, 201, 63, 0.9)';
        element.style.cssText = `background: ${bgColor}; color: #fff; padding: 12px 20px; border-radius: 8px; font-size: 0.9rem; box-shadow: 0 4px 12px rgba(0,0,0,0.3); backdrop-filter: blur(10px);`;
        element.innerText = message;
        container.appendChild(element);
        
        setTimeout(() => {
            element.style.opacity = '0';
            setTimeout(() => element.remove(), 300);
        }, 4000);
    }
};

const nav = {
    switchTab(targetViewId, element) {
        document.querySelectorAll('.view-section').forEach(view => view.classList.add('hidden'));
        document.getElementById(targetViewId).classList.remove('hidden');
        document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
        if (element) element.classList.add('active');
    }
};

const deployFlow = {
    handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (e) => {
            document.getElementById('scriptInput').value = e.target.result;
            document.getElementById('filename-display').innerText = file.name;
            toast.show(`File ${file.name} loaded.`);
        };
        reader.readAsText(file);
    },

    async nextToOTP() {
        const phone = document.getElementById('phoneInput').value.trim();
        const script = document.getElementById('scriptInput').value.trim();
        const btn = document.getElementById('btn-deploy');

        if (!phone || !script) return toast.show('Phone and script are required.', 'error');

        AppState.phone = phone;
        btn.classList.add('loading');

        try {
            const res = await fetch('/api/deploy/initiate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone: phone, script: script })
            });
            const data = await res.json();
            btn.classList.remove('loading');

            if (data.status === 'awaiting_otp') {
                this.goBack('step1-script', 'step2-otp');
                toast.show('Request sent. Waiting for OTP.');
            } else {
                toast.show(data.message || 'Error', 'error');
            }
        } catch (e) {
            btn.classList.remove('loading');
            toast.show('Network error.', 'error');
        }
    },

    async nextToPassword() {
        const otpCode = document.getElementById('otpInput').value.trim();
        const btn = document.getElementById('btn-otp');
        if (!otpCode) return toast.show('Enter OTP.', 'error');
        btn.classList.add('loading');

        try {
            const res = await fetch('/api/deploy/verify-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone: AppState.phone, code: otpCode })
            });
            const data = await res.json();
            btn.classList.remove('loading');

            if (data.status === 'awaiting_2fa') {
                this.goBack('step2-otp', 'step3-password');
                toast.show('2FA Required.');
            } else if (data.status === 'deployed') {
                this.success();
            } else {
                toast.show(data.message || 'Verification failed.', 'error');
            }
        } catch (e) {
            btn.classList.remove('loading');
            toast.show('Network error.', 'error');
        }
    },

    async finalize() {
        const password = document.getElementById('passwordInput').value;
        const btn = document.getElementById('btn-pass');
        btn.classList.add('loading');

        try {
            const res = await fetch('/api/deploy/finalize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone: AppState.phone, password: password })
            });
            const data = await res.json();
            btn.classList.remove('loading');

            if (data.status === 'deployed') {
                this.success();
            } else {
                toast.show(data.message || 'Incorrect Password.', 'error');
            }
        } catch (e) {
            btn.classList.remove('loading');
            toast.show('Network error.', 'error');
        }
    },

    success() {
        document.getElementById('step2-otp').classList.add('hidden');
        document.getElementById('step3-password').classList.add('hidden');
        document.getElementById('step4-success').classList.remove('hidden');
        
        const fileName = document.getElementById('filename-display').innerText;
        const safeId = AppState.phone.replace(/[^0-9]/g, ''); 
        
        AppState.activeBots[safeId] = { phoneKey: AppState.phone, name: fileName, status: 'Running' };
        this.renderBots();
        toast.show('Bot Deployed!', 'success');
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
    },

    renderBots() {
        const container = document.querySelector('#view-files .glass-panel');
        let html = '<div class="panel-header"><h2>Your Bots</h2></div>';
        
        for (const [id, bot] of Object.entries(AppState.activeBots)) {
            const isRunning = bot.status === 'Running';
            html += `
            <div class="file-item">
                <div class="file-info-header">
                    <div>
                        <div class="file-name">${bot.name}</div>
                        <div class="file-status">${isRunning ? 'Online' : 'Offline'}</div>
                    </div>
                    <span class="status-dot ${isRunning ? 'green pulse' : 'red'}">●</span>
                </div>
                <div class="file-actions">
                    <button class="action-btn" onclick="terminal.open('${bot.phoneKey}', '${bot.name}')">📝 Logs</button>
                    ${isRunning ? 
                        `<button class="action-btn danger" onclick="botControl.sendAction('${id}', '${bot.phoneKey}', 'stop')">⏹ Stop</button>` :
                        `<button class="action-btn danger" onclick="botControl.deleteLocal('${id}')">🗑 Delete</button>`
                    }
                </div>
            </div>`;
        }
        if(Object.keys(AppState.activeBots).length === 0) html += "<p>No bots active.</p>";
        container.innerHTML = html;
    }
};

const botControl = {
    async sendAction(botId, phoneKey, actionName) {
        toast.show(`Sending ${actionName}...`);
        try {
            const res = await fetch('/api/bot/control', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone: phoneKey, action: actionName })
            });
            const data = await res.json();
            if (data.status === 'stopped') {
                AppState.activeBots[botId].status = 'Stopped';
                deployFlow.renderBots();
                toast.show(`Bot stopped.`);
            }
        } catch (e) {
            toast.show('Network error.', 'error');
        }
    },
    deleteLocal(botId) {
        delete AppState.activeBots[botId];
        deployFlow.renderBots();
    }
};

const terminal = {
    async open(phoneKey, botName) {
        document.getElementById('terminal-modal').classList.remove('hidden');
        document.getElementById('terminal-bot-name').innerText = botName;
        const output = document.getElementById('terminal-output');
        output.innerHTML = "<p>Fetching logs...</p>";
        
        try {
            const res = await fetch('/api/bot/control', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone: phoneKey, action: 'logs' })
            });
            const data = await res.json();
            output.innerHTML = `<pre>${data.logs || 'No logs'}</pre>`;
        } catch (e) {
            output.innerHTML = "<p style='color:red;'>Error fetching logs.</p>";
        }
        output.scrollTop = output.scrollHeight;
    },
    close() {
        document.getElementById('terminal-modal').classList.add('hidden');
    }
};
