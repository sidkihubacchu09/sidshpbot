// Local Database Seed Initialization
if (!localStorage.getItem('sid_initialized')) {
    const defaultBots = [
        { id: 'bot_1', name: 'auto_reply.py', status: 'Running', uptime: '4h 12m', ram: '12MB' },
        { id: 'bot_2', name: 'scraper_bot.py', status: 'Stopped', uptime: '0m', ram: '0MB' }
    ];
    localStorage.setItem('sid_bots', JSON.stringify(defaultBots));
    localStorage.setItem('sid_wallet', '0.00');
    localStorage.setItem('sid_premium', 'false');
    localStorage.setItem('sid_bg_video', 'https://cdn.pixabay.com/video/2020/05/25/40131-424785461_large.mp4');
    localStorage.setItem('sid_initialized', 'true');
}

// Global Core State Navigation
const nav = {
    switchTab: function(tabId, element) {
        // Hide all views safely
        document.querySelectorAll('.view-section').forEach(section => {
            section.classList.add('hidden');
            section.classList.remove('active');
        });
        
        // Render target view
        const target = document.getElementById(tabId);
        if (target) {
            target.classList.remove('hidden');
            target.classList.add('active');
        }

        // Active state styling updates
        document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
        if (element) {
            element.classList.add('active');
        } else {
            // Internal mapping context correction
            const indexMap = { 'view-deploy': 1, 'view-files': 2, 'view-settings': 3, 'view-admin': 4 };
            const itemEl = document.querySelector(`.glass-nav .nav-item:nth-child(${indexMap[tabId]})`);
            if (itemEl) itemEl.classList.add('active');
        }

        // Refresh views natively if looking at file assets
        if (tabId === 'view-files') {
            renderBotDashboard();
        }
    }
};

// Orchestrated Connection Flow Engine
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
        const script = document.getElementById('scriptInput').value;

        if (!phone) {
            alert('Please provide a valid connection phone number.');
            return;
        }

        const btn = document.getElementById('btn-deploy');
        btn.classList.add('loading');

        setTimeout(() => {
            btn.classList.remove('loading');
            this.tempData.phone = phone;
            this.tempData.script = script;

            document.getElementById('otp-phone-display').innerText = `We sent a login code to ${phone}`;
            document.getElementById('step1-script').classList.add('hidden');
            document.getElementById('step2-otp').classList.remove('hidden');
        }, 1500);
    },

    nextToPassword: function() {
        const otp = document.getElementById('otpInput').value;
        if (!otp) {
            alert('Please type the Telegram verification matrix code.');
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
            
            // Push script deployment execution directly to LocalDB Storage
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

// UI Dashboard Generation Engine
function renderBotDashboard() {
    const bots = JSON.parse(localStorage.getItem('sid_bots') || '[]');
    const container = document.getElementById('view-files').querySelector('.glass-panel');
    
    // Calculate node run distribution metrics
    const totalBots = bots.length;
    const runningBots = bots.filter(b => b.status === 'Running').length;

    // Reset layout frame
    container.innerHTML = `
        <div class="panel-header" style="display: flex; justify-content: space-between; align-items: center;">
            <h2>Your Bots</h2>
            <span style="font-size: 0.8rem; background: rgba(39, 201, 63, 0.2); color: #27c93f; padding: 5px 12px; border-radius: 20px; border: 1px solid rgba(39, 201, 63, 0.4); font-weight: bold;">
                🟢 ${runningBots} / ${totalBots} Running
            </span>
        </div>
        <p class="status-text">Manage your hosted userbot processes.</p>
    `;

    if(bots.length === 0) {
        container.innerHTML += `<p style="text-align:center; color:var(--text-muted); padding:20px;">No bots deployed to this server node.</p>`;
        return;
    }

    bots.forEach((bot, index) => {
        const isRunning = bot.status === 'Running';
        const itemHtml = `
            <div class="file-item" style="animation: fadeInUp 0.4s ease forwards; animation-delay: ${index * 0.1}s;">
                <div class="file-info-header">
                    <div>
                        <div class="file-name" style="${!isRunning ? 'color:#ccc;' : ''}">${bot.name}</div>
                        <div class="file-status">${bot.status} • Uptime: ${bot.uptime} • ${bot.ram} RAM</div>
                    </div>
                    <span class="status-dot ${isRunning ? 'green pulse' : 'red'}">●</span>
                </div>
                <div class="file-actions">
                    <button class="action-btn" onclick="terminal.open('${bot.name}')">📝 Logs</button>
                    <button class="action-btn" onclick="toggleBotState('${bot.id}')">${isRunning ? '🔄 Restart' : '▶ Start'}</button>
                    <button class="action-btn danger" onclick="deleteBotAsset('${bot.id}')">${isRunning ? '⏹ Stop' : '🗑 Delete'}</button>
                </div>
            </div>
        `;
        container.innerHTML += itemHtml;
    });
}

// Runtime Core Control Operations
function toggleBotState(botId) {
    let bots = JSON.parse(localStorage.getItem('sid_bots') || '[]');
    bots = bots.map(b => {
        if(b.id === botId) {
            const running = b.status === 'Running';
            b.status = running ? 'Stopped' : 'Running';
            b.uptime = running ? '0m' : '1m';
            b.ram = running ? '0MB' : '14MB';
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
        // Safe check: If running, turn off process before actual asset deletion
        toggleBotState(botId);
        return;
    }

    bots = bots.filter(b => b.id !== botId);
    localStorage.setItem('sid_bots', JSON.stringify(bots));
    renderBotDashboard();
}

// Live Terminal Simulation Module
let logInterval = null;
const terminal = {
    open: function(botName) {
        const modal = document.getElementById('terminal-modal');
        document.getElementById('terminal-bot-name').innerText = `logs::${botName}`;
        const output = document.getElementById('terminal-output');
        output.innerHTML = '';
        modal.classList.remove('hidden');

        const mockLogs = [
            `[INFO] Initializing client sequence for asset: ${botName}...`,
            `[INFO] Connecting to core cloud container layer...`,
            `[SUCCESS] DB connection verified. Loading Telethon runtime core parameters.`,
            `[INFO] Client runtime authenticated. Listening for incoming interface requests...`,
            `[METRIC] CPU performance stabilization complete. Ram usage stable.`
        ];

        mockLogs.forEach(log => output.innerHTML += `<div>${log}</div>`);

        // Generate processing running loop logs
        logInterval = setInterval(() => {
            const randomEvents = [
                `[UPDATE] Checked cloud update triggers - status up to date.`,
                `[DEBUG] Database synced parameters successfully with main frame.`,
                `[METRIC] Health check OK. Internal latency status: 14ms.`,
                `[INFO] Anti-flood protection layer standing by.`
            ];
            const logEntry = randomEvents[Math.floor(Math.random() * randomEvents.length)];
            output.innerHTML += `<div>${logEntry}</div>`;
            output.scrollTop = output.scrollHeight;
        }, 2200);
    },
    close: function() {
        document.getElementById('terminal-modal').classList.add('hidden');
        if(logInterval) clearInterval(logInterval);
    }
};

// Settings Panel Application State Sync
const appSettings = {
    loadDashboard: function() {
        const premiumActive = localStorage.getItem('sid_premium') === 'true';
        const walletBalance = localStorage.getItem('sid_wallet') || '0.00';
        const currentBg = localStorage.getItem('sid_bg_video');

        // Dynamically adjust elements within preference views
        const statusEl = document.querySelector('#view-settings span[style*="font-weight: bold;"]');
        if(statusEl) {
            statusEl.innerText = premiumActive ? '💎 Premium Pro Account' : 'Standard (Free)';
            statusEl.style.color = premiumActive ? '#ffd700' : '#fff';
        }

        const balanceEl = document.querySelector('#view-settings span[style*="color: #27c93f;"]');
        if(balanceEl) balanceEl.innerText = `$${walletBalance}`;

        const inputEl = document.getElementById('video-url-input');
        if(inputEl) inputEl.value = currentBg;

        // Upgrade functionality binding hook
        const upgradeBtn = document.querySelector('#view-settings button[style*="linear-gradient"]');
        if(upgradeBtn) {
            if(premiumActive) {
                upgradeBtn.innerText = '✅ Pro Access Activated';
                upgradeBtn.style.background = 'rgba(255,255,255,0.1)';
                upgradeBtn.style.color = '#ccc';
                upgradeBtn.disabled = true;
            } else {
                upgradeBtn.onclick = () => this.purchasePremium();
            }
        }
    },
    purchasePremium: function() {
        // Trigger simulated premium execution
        localStorage.setItem('sid_premium', 'true');
        localStorage.setItem('sid_wallet', '45.00'); // Seed allocation for simulation context
        alert('Payment authorized successfully! Welcome to SID HOSTING Premium!');
        this.loadDashboard();
    },
    updateVideo: function() {
        const newUrl = document.getElementById('video-url-input').value;
        if(newUrl) {
            localStorage.setItem('sid_bg_video', newUrl);
            const videoElement = document.getElementById('bg-video');
            if(videoElement) {
                videoElement.src = newUrl;
                videoElement.load();
            }
            alert('Global preference background updated successfully.');
        }
    }
};

// Global Boot Sequence Hooks
document.addEventListener('DOMContentLoaded', () => {
    // Sync master active background configuration target
    const savedBg = localStorage.getItem('sid_bg_video');
    if(savedBg) {
        const video = document.getElementById('bg-video');
        if(video && video.src !== savedBg) {
            video.src = savedBg;
        }
    }

    // Bind setting layout configurations
    appSettings.loadDashboard();

    // Map mutations to navbar intercept configurations safely
    const settingsTabBtn = document.querySelector('.glass-nav .nav-item:nth-child(3)');
    if(settingsTabBtn) {
        const nativeOnclick = settingsTabBtn.onclick;
        settingsTabBtn.onclick = function(e) {
            appSettings.loadDashboard();
            if(nativeOnclick) nativeOnclick.apply(this, arguments);
            else nav.switchTab('view-settings', this);
        };
    }
});
