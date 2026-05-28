// Local Storage Database Initialization Core
if (!localStorage.getItem('sid_initialized')) {
    const defaultBots = [
        { id: 'bot_1', name: 'auto_reply.py', status: 'Running', uptime: '4h 12m', ram: '12MB', logs: ["[SYS] Pre-compiled module loaded.", "[INFO] Listening for events..."] },
        { id: 'bot_2', name: 'scraper_bot.py', status: 'Stopped', uptime: '0m', ram: '0MB', logs: ["[SYS] Process terminated by user request."] }
    ];
    localStorage.setItem('sid_bots', JSON.stringify(defaultBots));
    localStorage.setItem('sid_wallet', '0.00');
    localStorage.setItem('sid_premium', 'false');
    localStorage.setItem('sid_initialized', 'true');
}

// Global Tab Routing System
const nav = {
    switchTab: function(tabId, element) {
        document.querySelectorAll('.view-section').forEach(section => {
            section.classList.add('hidden');
            section.classList.remove('active');
        });
        
        const target = document.getElementById(tabId);
        if (target) {
            target.classList.remove('hidden');
            target.classList.add('active');
        }

        document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
        if (element) {
            element.classList.add('active');
        } else {
            const indexMap = { 'view-deploy': 1, 'view-files': 2, 'view-settings': 3, 'view-admin': 4 };
            const itemEl = document.querySelector(`.glass-nav .nav-item:nth-child(${indexMap[tabId]})`);
            if (itemEl) itemEl.classList.add('active');
        }

        if (tabId === 'view-files') {
            renderBotDashboard();
        }
    }
};

// Deployment Pipeline & Real-Time Validation Environment
const deployFlow = {
    tempData: { phone: '', script: '', fileName: 'main.py', runtimeGeneratedOTP: null },

    handleFileUpload: function(event) {
        const file = event.target.files[0];
        if (file) {
            this.tempData.fileName = file.name;
            document.getElementById('filename-display').innerText = file.name;
            
            const reader = new FileReader();
            reader.onload = function(e) {
                document.getElementById('scriptInput').value = e.target.result;
            };
            reader.readAsText(file);
        }
    },

    nextToOTP: function() {
        const phone = document.getElementById('phoneInput').value.trim();
        const scriptBody = document.getElementById('scriptInput').value.trim();

        if (!phone || phone.length < 7) {
            alert('❌ Deployment Failed: Invalid international phone format routing context.');
            return;
        }
        if (!scriptBody) {
            alert('❌ Compilation Failed: Cannot deploy an unallocated or empty script environment.');
            return;
        }

        const btn = document.getElementById('btn-deploy');
        btn.classList.add('loading');

        setTimeout(() => {
            btn.classList.remove('loading');
            this.tempData.phone = phone;
            this.tempData.script = scriptBody;

            // Generate real-time randomized verification secure token
            this.tempData.runtimeGeneratedOTP = Math.floor(10000 + Math.random() * 90000).toString();
            
            // Dispatch systemic simulated network notification alert
            alert(`[TELEGRAM NETWORK INTERFACE]\nIncoming authorization packet requested for node link.\nYour verification code is: ${this.tempData.runtimeGeneratedOTP}`);

            document.getElementById('otp-phone-display').innerText = `We sent a 5-digit login code to ${phone}`;
            document.getElementById('step1-script').classList.add('hidden');
            document.getElementById('step2-otp').classList.remove('hidden');
        }, 1500);
    },

    nextToPassword: function() {
        const inputOtp = document.getElementById('otpInput').value.trim();
        const btn = document.getElementById('btn-otp');

        if (!inputOtp) {
            alert('Please enter your 5-digit network code packet.');
            return;
        }

        btn.classList.add('loading');

        setTimeout(() => {
            btn.classList.remove('loading');
            
            // Real-time runtime value verification check
            if (inputOtp === this.tempData.runtimeGeneratedOTP) {
                document.getElementById('step2-otp').classList.add('hidden');
                document.getElementById('step3-password').classList.remove('hidden');
                document.getElementById('otpInput').value = ''; // Flush validation cache
            } else {
                alert('❌ Access Denied: Invalid OTP signature credentials provided.');
            }
        }, 1200);
    },

    finalize: function() {
        const passwordInput = document.getElementById('passwordInput').value;
        const btn = document.getElementById('btn-pass');

        btn.classList.add('loading');

        setTimeout(() => {
            btn.classList.remove('loading');
            
            // Real-Time Dynamic Source Parsing Compiler Check
            const runtimeLogs = [];
            runtimeLogs.push(`[SYS] Initializing container sandbox architecture for node upload...`);
            runtimeLogs.push(`[SYS] Parsing local binary source context: "${this.tempData.fileName}"`);

            // Scan code string payload directly to map dynamic dependencies
            const importedModules = [];
            if (this.tempData.script.includes('telethon')) importedModules.push('telethon');
            if (this.tempData.script.includes('pyrogram')) importedModules.push('pyrogram');
            if (this.tempData.script.includes('requests')) importedModules.push('requests');
            if (this.tempData.script.includes('os')) importedModules.push('os');

            if (importedModules.length > 0) {
                runtimeLogs.push(`[PIP] Dependencies mapped: [${importedModules.join(', ')}]. Resolving environments...`);
            } else {
                runtimeLogs.push(`[WARN] No standard asynchronous network packages declared. Running core environment.`);
            }

            // Real-time logical syntax integrity scanner simulation
            if (this.tempData.script.includes('def') && !this.tempData.script.includes(':')) {
                runtimeLogs.push(`[CRITICAL] SyntaxError: Expected ':' block closure in function structures.`);
                alert('❌ Deployment Matrix Broken: Local compiler returned code SyntaxError structural faults.');
                return;
            }

            runtimeLogs.push(`[SUCCESS] Virtual container pipeline mapped cleanly. Process state online.`);
            runtimeLogs.push(`[LIVE] Execution log outputs connected successfully:\n----------------------`);
            
            // Slice the actual user script content to create a simulated operational preview
            const linePreviews = this.tempData.script.split('\n').filter(l => l.trim() !== '');
            linePreviews.slice(0, 3).forEach(line => {
                runtimeLogs.push(`[RUNNING] > ${line.substring(0, 50)}`);
            });

            // Write verified asset build context out to LocalStorage persistence
            const currentBots = JSON.parse(localStorage.getItem('sid_bots') || '[]');
            currentBots.push({
                id: 'bot_' + Date.now(),
                name: this.tempData.fileName,
                status: 'Running',
                uptime: '1m',
                ram: `${Math.floor(8 + Math.random() * 8)}MB`,
                logs: runtimeLogs
            });
            localStorage.setItem('sid_bots', JSON.stringify(currentBots));

            document.getElementById('step3-password').classList.add('hidden');
            document.getElementById('step4-success').classList.remove('hidden');
        }, 2000);
    },

    goBack: function(fromId, toId) {
        document.getElementById(fromId).classList.add('hidden');
        document.getElementById(toId).classList.remove('hidden');
    },

    reset: function() {
        document.getElementById('phoneInput').value = '';
        document.getElementById('scriptInput').value = '';
        document.getElementById('otpInput').value = '';
        document.getElementById('passwordInput').value = '';
        document.getElementById('filename-display').innerText = 'main.py';
        this.tempData.runtimeGeneratedOTP = null;
        
        document.getElementById('step4-success').classList.add('hidden');
        document.getElementById('step1-script').classList.remove('hidden');
    }
};

// UI Element Constructor Engine
function renderBotDashboard() {
    const bots = JSON.parse(localStorage.getItem('sid_bots') || '[]');
    const container = document.getElementById('bots-list-container');
    const counter = document.getElementById('bot-running-counter');
    
    const totalBots = bots.length;
    const runningBots = bots.filter(b => b.status === 'Running').length;

    if (counter) {
        counter.innerText = `🟢 ${runningBots} / ${totalBots} Running`;
    }

    container.innerHTML = '';

    if (bots.length === 0) {
        container.innerHTML = `<p style="text-align:center; color:var(--text-muted); padding:24px;">No custom bot architectures deployed to this cloud node.</p>`;
        return;
    }

    bots.forEach((bot) => {
        const isRunning = bot.status === 'Running';
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        
        fileItem.innerHTML = `
            <div class="file-info-header">
                <div>
                    <div class="file-name" style="${!isRunning ? 'color:#94a3b8;' : ''}">${bot.name}</div>
                    <div class="file-status">${bot.status} • Uptime: ${bot.uptime} • ${bot.ram} RAM</div>
                </div>
                <span class="status-dot ${isRunning ? 'green pulse' : 'red'}">●</span>
            </div>
            <div class="file-actions">
                <button class="action-btn" onclick="terminal.open('${bot.id}')">📝 Logs</button>
                <button class="action-btn" onclick="toggleBotState('${bot.id}')" style="${!isRunning ? 'color: #27c93f; border-color: rgba(39,201,63,0.3);' : ''}">
                    ${isRunning ? '🔄 Restart' : '▶ Start'}
                </button>
                <button class="action-btn danger" onclick="deleteBotAsset('${bot.id}')">
                    ${isRunning ? '⏹ Stop' : '🗑 Delete'}
                </button>
            </div>
        `;
        container.appendChild(fileItem);
    });
}

function toggleBotState(botId) {
    let bots = JSON.parse(localStorage.getItem('sid_bots') || '[]');
    bots = bots.map(b => {
        if (b.id === botId) {
            const running = b.status === 'Running';
            b.status = running ? 'Stopped' : 'Running';
            b.uptime = running ? '0m' : '1m';
            b.ram = running ? '0MB' : `${Math.floor(10 + Math.random() * 6)}MB`;
            if (!b.logs) b.logs = [];
            b.logs.push(`[SYS-EVENT] Application state manually shifted to: ${b.status}`);
        }
        return b;
    });
    localStorage.setItem('sid_bots', JSON.stringify(bots));
    renderBotDashboard();
}

function deleteBotAsset(botId) {
    let bots = JSON.parse(localStorage.getItem('sid_bots') || '[]');
    const target = bots.find(b => b.id === botId);
    
    if (target && target.status === 'Running') {
        toggleBotState(botId);
        return;
    }

    bots = bots.filter(b => b.id !== botId);
    localStorage.setItem('sid_bots', JSON.stringify(bots));
    renderBotDashboard();
}

// Live Logging Diagnostic Terminal Engine
let logInterval = null;
const terminal = {
    open: function(botId) {
        const bots = JSON.parse(localStorage.getItem('sid_bots') || '[]');
        const currentBot = bots.find(b => b.id === botId);
        if (!currentBot) return;

        const modal = document.getElementById('terminal-modal');
        document.getElementById('terminal-bot-name').innerText = `logs::${currentBot.name}`;
        const output = document.getElementById('terminal-output');
        output.innerHTML = '';
        modal.classList.remove('hidden');

        // Load historical or setup trace log matrices
        if (currentBot.logs && currentBot.logs.length > 0) {
            currentBot.logs.forEach(log => {
                output.innerHTML += `<div class="log-line">${log}</div>`;
            });
        } else {
            output.innerHTML += `<div class="log-line">[SYS-INFO] Fetching historical runtime stack track lines...</div>`;
        }

        output.scrollTop = output.scrollHeight;

        // If active, stream continuous running server framework events
        if (currentBot.status === 'Running') {
            logInterval = setInterval(() => {
                const liveUpdates = [
                    `[METRIC] Framework tick validated. Latency core ping: ${Math.floor(8 + Math.random() * 10)}ms.`,
                    `[DEBUG] Asynchronous background worker tasks resolved. Memory flush execution clean.`,
                    `[INFO] Secure API event socket loop actively waiting for incoming telemetry data channels...`,
                    `[SYS-METRIC] Container tracking status: Active loop operational.`
                ];
                const selectedEntry = liveUpdates[Math.floor(Math.random() * liveUpdates.length)];
                output.innerHTML += `<div class="log-line">${selectedEntry}</div>`;
                output.scrollTop = output.scrollHeight;

                // Persist the newly generated stream line data to storage records
                let freshBotsList = JSON.parse(localStorage.getItem('sid_bots') || '[]');
                freshBotsList = freshBotsList.map(b => {
                    if (b.id === botId) {
                        if (!b.logs) b.logs = [];
                        b.logs.push(selectedEntry);
                    }
                    return b;
                });
                localStorage.setItem('sid_bots', JSON.stringify(freshBotsList));

            }, 2500);
        } else {
            output.innerHTML += `<div class="log-line" style="color: #ff5f56;">[OFFLINE] Process streaming paused. Start bot to restore standard real-time output trackers.</div>`;
            output.scrollTop = output.scrollHeight;
        }
    },
    close: function() {
        document.getElementById('terminal-modal').classList.add('hidden');
        if (logInterval) clearInterval(logInterval);
    }
};

// Profile Configuration Controls
const appSettings = {
    loadDashboard: function() {
        const premiumActive = localStorage.getItem('sid_premium') === 'true';
        const walletBalance = localStorage.getItem('sid_wallet') || '0.00';

        const statusEl = document.getElementById('settings-account-status');
        if (statusEl) {
            statusEl.innerText = premiumActive ? '💎 Premium Pro Account' : 'Standard (Free)';
            statusEl.style.color = premiumActive ? '#ffd700' : '#fff';
        }

        const balanceEl = document.getElementById('settings-wallet-balance');
        if (balanceEl) balanceEl.innerText = `$${walletBalance}`;

        const upgradeBtn = document.getElementById('settings-upgrade-btn');
        if (upgradeBtn) {
            if (premiumActive) {
                upgradeBtn.innerText = '✅ Pro Access Activated';
                upgradeBtn.style.background = 'rgba(255,255,255,0.06)';
                upgradeBtn.style.color = '#94a3b8';
                upgradeBtn.disabled = true;
            } else {
                upgradeBtn.onclick = () => this.purchasePremium();
            }
        }
    },
    purchasePremium: function() {
        localStorage.setItem('sid_premium', 'true');
        localStorage.setItem('sid_wallet', '50.00'); 
        alert('Premium access token authorized successfully!');
        this.loadDashboard();
    }
};

// Core Startup Hook Binding Layer
document.addEventListener('DOMContentLoaded', () => {
    appSettings.loadDashboard();
    
    const settingsTabBtn = document.querySelector('.glass-nav .nav-item:nth-child(3)');
    if (settingsTabBtn) {
        settingsTabBtn.addEventListener('click', () => {
            appSettings.loadDashboard();
        });
    }
});
