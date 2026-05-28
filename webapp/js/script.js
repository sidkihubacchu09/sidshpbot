// Local Storage Database Initialization Core
if (!localStorage.getItem('sid_initialized')) {
    const defaultBots = [
        { id: 'bot_1', name: 'auto_reply.py', status: 'Running', uptime: '4h 12m', ram: '12MB' },
        { id: 'bot_2', name: 'scraper_bot.py', status: 'Stopped', uptime: '0m', ram: '0MB' }
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

// Deployment Pipeline Framework
const deployFlow = {
    tempData: { phone: '', script: '', fileName: 'main.py' },

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
        const phone = document.getElementById('phoneInput').value;
        if (!phone) {
            alert('Please enter a valid phone number setup matrix configuration.');
            return;
        }

        const btn = document.getElementById('btn-deploy');
        btn.classList.add('loading');

        setTimeout(() => {
            btn.classList.remove('loading');
            this.tempData.phone = phone;
            this.tempData.script = document.getElementById('scriptInput').value;

            document.getElementById('otp-phone-display').innerText = `We sent a login code to ${phone}`;
            document.getElementById('step1-script').classList.add('hidden');
            document.getElementById('step2-otp').classList.remove('hidden');
        }, 1500);
    },

    nextToPassword: function() {
        const otp = document.getElementById('otpInput').value;
        if (!otp) {
            alert('Verification code matrix cannot remain blank.');
            return;
        }
        
        const btn = document.getElementById('btn-otp');
        btn.classList.add('loading');

        setTimeout(() => {
            btn.classList.remove('loading');
            document.getElementById('step2-otp').classList.add('hidden');
            document.getElementById('step3-password').classList.remove('hidden');
        }, 1200);
    },

    finalize: function() {
        const btn = document.getElementById('btn-pass');
        btn.classList.add('loading');

        setTimeout(() => {
            btn.classList.remove('loading');
            
            const currentBots = JSON.parse(localStorage.getItem('sid_bots') || '[]');
            currentBots.push({
                id: 'bot_' + Date.now(),
                name: this.tempData.fileName,
                status: 'Running',
                uptime: '1m',
                ram: '14MB'
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
                <button class="action-btn" onclick="terminal.open('${bot.name}')">📝 Logs</button>
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
            b.ram = running ? '0MB' : '12MB';
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
    open: function(botName) {
        const modal = document.getElementById('terminal-modal');
        document.getElementById('terminal-bot-name').innerText = `logs::${botName}`;
        const output = document.getElementById('terminal-output');
        output.innerHTML = '';
        modal.classList.remove('hidden');

        const initialLogs = [
            `[SYS-INFO] Registering process environment thread for: ${botName}...`,
            `[SYS-INFO] Virtual memory framework map verified successfully.`,
            `[SUCCESS] Session database handshakes authorized. Loading telethon.`,
            `[LIVE] Listening for dynamic incoming system gateway events...`
        ];

        initialLogs.forEach(log => output.innerHTML += `<div class="log-line">${log}</div>`);

        logInterval = setInterval(() => {
            const updates = [
                `[METRIC] Thread check OK. Latency ping rate: 11ms.`,
                `[DEBUG] State cache successfully flushed to dynamic container.`,
                `[INFO] Inbound filter matrices processed successfully.`,
                `[PROTECTION] Anti-flood delay parameters operating cleanly.`
            ];
            const randomEntry = updates[Math.floor(Math.random() * updates.length)];
            output.innerHTML += `<div class="log-line">${randomEntry}</div>`;
            output.scrollTop = output.scrollHeight;
        }, 2000);
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
