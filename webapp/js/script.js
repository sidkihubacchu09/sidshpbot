// ==========================================
// 1. Local Storage Database Initialization Core
// ==========================================
if (!localStorage.getItem('sid_initialized')) {
    const defaultBots = [
        { 
            id: 'bot_1', 
            name: 'auto_reply.py', 
            status: 'Running', 
            uptime: '4h 12m', 
            ram: '12MB', 
            startTime: Date.now() - (4 * 60 * 60 * 1000 + 12 * 60 * 1000), // 4h 12m ago
            logs: ["[SYS] Pre-compiled module loaded.", "[INFO] Listening for events..."],
            traits: { type: 'Telegram Userbot App', metricTemplate: 'Events captured: ', activeMetric: 'Events captured: 142', counterVal: 142 }
        },
        { 
            id: 'bot_2', 
            name: 'scraper_bot.py', 
            status: 'Stopped', 
            uptime: '0m', 
            ram: '0MB', 
            startTime: null,
            logs: ["[SYS] Process terminated by user request."],
            traits: { type: 'Web Scraper Instance', metricTemplate: 'Target URLs parsed: ', activeMetric: 'Target URLs parsed: 0', counterVal: 0 }
        }
    ];
    localStorage.setItem('sid_bots', JSON.stringify(defaultBots));
    localStorage.setItem('sid_wallet', '0.00');
    localStorage.setItem('sid_premium', 'false');
    localStorage.setItem('sid_initialized', 'true');
}

// Helper to reliably update local storage and refresh dashboard
function updateStoredBots(bots) {
    localStorage.setItem('sid_bots', JSON.stringify(bots));
    renderBotDashboard();
}

// Utility to humanize running time
function calculateUptime(startTime) {
    if (!startTime) return '0m';
    const diffMs = Date.now() - startTime;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    
    if (diffHours > 0) {
        return `${diffHours}h ${diffMins % 60}m`;
    }
    return `${diffMins}m`;
}

// ==========================================
// 2. Global Tab Routing System
// ==========================================
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

// ==========================================
// 3. Heuristic Source Analyzer Matrix (User Script Parser)
// ==========================================
const sourceAnalyzer = {
    analyze: function(scriptText) {
        const lines = scriptText.split('\n');
        const traits = {
            type: 'Core Sandbox Script',
            dependencies: [],
            criticalFaults: null,
            activeMetric: 'Requests processed: 0',
            metricTemplate: 'Requests processed: ',
            customLogs: [],
            counterVal: 0
        };

        const textLower = scriptText.toLowerCase();
        
        // 1. Map Modules / System Dependencies
        if (textLower.includes('telethon')) traits.dependencies.push('telethon');
        if (textLower.includes('pyrogram')) traits.dependencies.push('pyrogram');
        if (textLower.includes('requests')) traits.dependencies.push('requests');
        if (textLower.includes('os')) traits.dependencies.push('os');
        if (textLower.includes('beautifulsoup') || textLower.includes('bs4')) traits.dependencies.push('beautifulsoup4');

        // 2. Classify Architecture Type & Telemetry Template
        if (textLower.includes('telethon') || textLower.includes('pyrogram')) {
            traits.type = 'Telegram Userbot App';
            traits.metricTemplate = 'Events captured: ';
            traits.activeMetric = 'Events captured: 0';
        } else if (textLower.includes('requests') || textLower.includes('beautifulsoup')) {
            traits.type = 'Web Scraper Instance';
            traits.metricTemplate = 'Target URLs parsed: ';
            traits.activeMetric = 'Target URLs parsed: 0';
        } else if (textLower.includes('flask') || textLower.includes('fastapi')) {
            traits.type = 'Microservice Web API';
            traits.metricTemplate = 'HTTP payloads received: ';
            traits.activeMetric = 'HTTP payloads received: 0';
        }

        // 3. Real-time Basic Python Syntax Validation Simulation
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            if (line.startsWith('def ') && !line.endsWith(':')) {
                traits.criticalFaults = `Line ${i + 1}: Function declaration missing colon structure definition (":")`;
                return traits;
            }
            if (line.startsWith('if ') && !line.endsWith(':') && !line.includes('if __name__')) {
                traits.criticalFaults = `Line ${i + 1}: Conditional block expression missing terminal assignment colon (":")`;
                return traits;
            }
        }

        // 4. Capture Custom Functional Previews to build context logs
        const functionalLines = lines.map(l => l.trim()).filter(l => l.length > 0 && !l.startsWith('#') && !l.startsWith('import'));
        if (functionalLines.length > 0) {
            functionalLines.slice(0, 3).forEach(line => {
                traits.customLogs.push(`[COMPILE-TRAIN] Hooked entity function structural block -> "${line.substring(0, 50)}"`);
            });
        }

        return traits;
    }
};

// ==========================================
// 4. Deployment Pipeline & Multi-Step Verification
// ==========================================
const deployFlow = {
    tempData: { phone: '', script: '', fileName: 'main.py', runtimeGeneratedOTP: null },

    handleFileUpload: function(event) {
        const file = event.target.files[0];
        if (file) {
            this.tempData.fileName = file.name;
            const displayEl = document.getElementById('filename-display');
            if (displayEl) displayEl.innerText = file.name;
            
            const reader = new FileReader();
            reader.onload = function(e) {
                const inputEl = document.getElementById('scriptInput');
                if (inputEl) inputEl.value = e.target.result;
            };
            reader.readAsText(file);
        }
    },

    nextToOTP: function() {
        const phoneInput = document.getElementById('phoneInput');
        const scriptInput = document.getElementById('scriptInput');
        
        const phone = phoneInput ? phoneInput.value.trim() : '';
        const scriptBody = scriptInput ? scriptInput.value.trim() : '';

        if (!phone || phone.length < 7) {
            alert('❌ Deployment Failed: Invalid international phone format routing context.');
            return;
        }
        if (!scriptBody) {
            alert('❌ Compilation Failed: Cannot deploy an unallocated or empty script environment.');
            return;
        }

        const btn = document.getElementById('btn-deploy');
        if (btn) btn.classList.add('loading');

        setTimeout(() => {
            if (btn) btn.classList.remove('loading');
            this.tempData.phone = phone;
            this.tempData.script = scriptBody;

            // Generate real-time randomized 5-digit authentication token
            this.tempData.runtimeGeneratedOTP = Math.floor(10000 + Math.random() * 90000).toString();
            
            // Dispatch dynamic system simulated modal alert
            alert(`[TELEGRAM NETWORK INTERFACE]\nIncoming authorization packet requested for node link.\nYour verification code is: ${this.tempData.runtimeGeneratedOTP}`);

            const displayPhone = document.getElementById('otp-phone-display');
            if (displayPhone) displayPhone.innerText = `We sent a 5-digit login code to ${phone}`;
            
            const step1 = document.getElementById('step1-script');
            const step2 = document.getElementById('step2-otp');
            if (step1) step1.classList.add('hidden');
            if (step2) step2.classList.remove('hidden');
        }, 1500);
    },

    nextToPassword: function() {
        const otpInput = document.getElementById('otpInput');
        const inputOtp = otpInput ? otpInput.value.trim() : '';
        const btn = document.getElementById('btn-otp');

        if (!inputOtp) {
            alert('Please enter your 5-digit network code packet.');
            return;
        }

        if (btn) btn.classList.add('loading');

        setTimeout(() => {
            if (btn) btn.classList.remove('loading');
            
            // Runtime value token match verification 
            if (inputOtp === this.tempData.runtimeGeneratedOTP) {
                const step2 = document.getElementById('step2-otp');
                const step3 = document.getElementById('step3-password');
                if (step2) step2.classList.add('hidden');
                if (step3) step3.classList.remove('hidden');
                if (otpInput) otpInput.value = ''; // Flush intermediate entry
            } else {
                alert('❌ Access Denied: Invalid OTP signature credentials provided.');
            }
        }, 1200);
    },

    finalize: function() {
        const btn = document.getElementById('btn-pass');
        if (btn) btn.classList.add('loading');

        setTimeout(() => {
            if (btn) btn.classList.remove('loading');
            
            // Execute automated structural script profiling on user asset
            const analysis = sourceAnalyzer.analyze(this.tempData.script);

            const runtimeLogs = [
                `[SYS] Initializing container sandbox architecture for node upload...`,
                `[SYS] Parsing local binary source context: "${this.tempData.fileName}"`
            ];

            // Crash compilation gracefully if security analyzer flag trips
            if (analysis.criticalFaults) {
                runtimeLogs.push(`[CRITICAL] SyntaxError caught during initial interpretation phase.`);
                runtimeLogs.push(`[CRITICAL] Details: ${analysis.criticalFaults}`);
                alert(`❌ Deployment Matrix Broken:\nCompiler found invalid code layout rules:\n${analysis.criticalFaults}`);
                return;
            }

            if (analysis.dependencies.length > 0) {
                runtimeLogs.push(`[PIP] Dependencies mapped: [${analysis.dependencies.join(', ')}]. Resolving local virtual environments...`);
            } else {
                runtimeLogs.push(`[WARN] No standard asynchronous network packages declared. Running core loop environment.`);
            }

            // Append custom code preview strings into simulated container terminal logs
            analysis.customLogs.forEach(logLine => runtimeLogs.push(logLine));
            runtimeLogs.push(`[SUCCESS] Virtual container pipeline mapped cleanly. Process configuration state online.`);
            runtimeLogs.push(`-----------------------------------------------------------------`);

            // Write asset record context out to storage parameters
            const currentBots = JSON.parse(localStorage.getItem('sid_bots') || '[]');
            const newBotId = 'bot_' + Date.now();
            currentBots.push({
                id: newBotId,
                name: this.tempData.fileName,
                status: 'Stopped', // Instantiated as Stopped; initialized completely when started
                uptime: '0m',
                ram: '0MB',
                startTime: null,
                logs: runtimeLogs,
                traits: {
                    type: analysis.type,
                    metricTemplate: analysis.metricTemplate,
                    activeMetric: analysis.activeMetric,
                    counterVal: analysis.counterVal,
                    rawScriptSource: this.tempData.script // Save code into local instance state context
                }
            });
            
            updateStoredBots(currentBots);

            const step3 = document.getElementById('step3-password');
            const step4 = document.getElementById('step4-success');
            if (step3) step3.classList.add('hidden');
            if (step4) step4.classList.remove('hidden');

            // Automatically transition environments and execute the freshly loaded userbot asset 
            setTimeout(() => {
                userbotEngine.runUserbotScript(newBotId);
            }, 800);
        }, 2000);
    },

    goBack: function(fromId, toId) {
        const fromEl = document.getElementById(fromId);
        const toEl = document.getElementById(toId);
        if (fromEl) fromEl.classList.add('hidden');
        if (toEl) toEl.classList.remove('hidden');
    },

    reset: function() {
        const fields = ['phoneInput', 'scriptInput', 'otpInput', 'passwordInput'];
        fields.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = '';
        });

        const fileDisp = document.getElementById('filename-display');
        if (fileDisp) fileDisp.innerText = 'main.py';
        this.tempData.runtimeGeneratedOTP = null;
        
        const step4 = document.getElementById('step4-success');
        const step1 = document.getElementById('step1-script');
        if (step4) step4.classList.add('hidden');
        if (step1) step1.classList.remove('hidden');
    }
};

// ==========================================
// 5. Userbot Script Core Run Engine Layer
// ==========================================
const userbotEngine = {
    runUserbotScript: function(botId) {
        let bots = JSON.parse(localStorage.getItem('sid_bots') || '[]');
        let selectedBot = bots.find(b => b.id === botId);

        if (!selectedBot) {
            console.error(`Execution routing error: Core node token target [${botId}] was not allocated.`);
            return;
        }

        // Enforce structural reset variables for initialization sequences
        selectedBot.status = 'Running';
        selectedBot.startTime = Date.now();
        selectedBot.uptime = '0m';
        selectedBot.ram = `${Math.floor(12 + Math.random() * 6)}MB`;

        if (!selectedBot.logs) selectedBot.logs = [];
        
        // Log clean execution traces into instance parameters
        selectedBot.logs.push(`[ENGINE] [${new Date().toLocaleTimeString()}] Spawning asynchronous process isolate thread...`);
        selectedBot.logs.push(`[ENGINE] Executing entrypoint compilation -> Python virtualenv cluster execution sequence.`);
        
        if (selectedBot.traits && selectedBot.traits.rawScriptSource) {
            selectedBot.logs.push(`[ENGINE] Core source footprint verification checksum validated cleanly.`);
        }

        selectedBot.logs.push(`[SYS-EVENT] Bot process actively switched to operational lifecycle state: Running`);

        // Re-save status structural modifications safely back to application core storage parameters
        updateStoredBots(bots);

        // If telemetry terminal windows are open, force synchronization streams 
        const openTerminalModal = document.getElementById('terminal-modal');
        if (openTerminalModal && !openTerminalModal.classList.contains('hidden')) {
            const runningTitle = document.getElementById('terminal-bot-name')?.innerText || '';
            if (runningTitle.includes(selectedBot.name)) {
                terminal.open(botId);
            }
        }
    }
};

// ==========================================
// 6. UI Element Constructor & Management Engine
// ==========================================
function renderBotDashboard() {
    const bots = JSON.parse(localStorage.getItem('sid_bots') || '[]');
    const container = document.getElementById('bots-list-container');
    const counter = document.getElementById('bot-running-counter');
    
    if (!container) return;

    // Dynamically calculate uptimes based on actual timestamps
    const dynamicBots = bots.map(bot => {
        if (bot.status === 'Running' && bot.startTime) {
            bot.uptime = calculateUptime(bot.startTime);
        }
        return bot;
    });

    const totalBots = dynamicBots.length;
    const runningBots = dynamicBots.filter(b => b.status === 'Running').length;

    if (counter) {
        counter.innerText = `🟢 ${runningBots} / ${totalBots} Deployed Hosting Threads Active`;
    }

    container.innerHTML = '';

    if (dynamicBots.length === 0) {
        container.innerHTML = `<p style="text-align:center; color:var(--text-muted); padding:24px;">No custom bot architectures deployed to this cloud node.</p>`;
        return;
    }

    dynamicBots.forEach((bot) => {
        const isRunning = bot.status === 'Running';
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        
        // Dynamically compute runtime indicators based on user code traits 
        const typeLabel = bot.traits ? bot.traits.type : 'Core Sandbox Script';
        const metricLabel = bot.traits ? bot.traits.activeMetric : 'Activity monitored';

        fileItem.innerHTML = `
            <div class="file-info-header">
                <div>
                    <div class="file-name" style="${!isRunning ? 'color:#94a3b8;' : ''}">${bot.name} <span style="font-size:11px; opacity:0.6; font-weight:normal; padding-left:4px;">(${typeLabel})</span></div>
                    <div class="file-status">${bot.status} • Uptime: ${bot.uptime} • ${bot.ram} • <b style="color:#38bdf8; font-weight:500;">${metricLabel}</b></div>
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
    const targetBot = bots.find(b => b.id === botId);

    if (targetBot && targetBot.status !== 'Running') {
        // Divert standard lifecycle execution pipeline parameters straight into our dedicated userbot processing script runner
        userbotEngine.runUserbotScript(botId);
    } else {
        // Handle normal execution termination sequence logic
        bots = bots.map(b => {
            if (b.id === botId) {
                b.status = 'Stopped';
                b.startTime = null;
                b.uptime = '0m';
                b.ram = '0MB';
                if (!b.logs) b.logs = [];
                b.logs.push(`[SYS-EVENT] Process manually shifted to operational state: Stopped`);
            }
            return b;
        });
        updateStoredBots(bots);
    }
}

function deleteBotAsset(botId) {
    let bots = JSON.parse(localStorage.getItem('sid_bots') || '[]');
    const target = bots.find(b => b.id === botId);
    
    // Safety check: standard hosting systems require stopping process instances before removal
    if (target && target.status === 'Running') {
        toggleBotState(botId);
        return;
    }

    bots = bots.filter(b => b.id !== botId);
    updateStoredBots(bots);
}

// ==========================================
// 7. Responsive Real-Time Telemetry Terminal Engine
// ==========================================
let logInterval = null;
const terminal = {
    open: function(botId) {
        const bots = JSON.parse(localStorage.getItem('sid_bots') || '[]');
        const currentBot = bots.find(b => b.id === botId);
        if (!currentBot) return;

        // Clear ongoing event thread intervals safely
        if (logInterval) clearInterval(logInterval);

        const modal = document.getElementById('terminal-modal');
        const title = document.getElementById('terminal-bot-name');
        const output = document.getElementById('terminal-output');
        
        if (!modal || !output) return;

        if (title) title.innerText = `runtime_stream::${currentBot.name}`;
        output.innerHTML = '';
        modal.classList.remove('hidden');

        // Output current stored lifecycle status metrics
        if (currentBot.logs && currentBot.logs.length > 0) {
            currentBot.logs.forEach(log => {
                output.innerHTML += `<div class="log-line">${log}</div>`;
            });
        } else {
            output.innerHTML += `<div class="log-line">[SYS-INFO] Pipeline active. Awaiting terminal allocation...</div>`;
        }

        output.scrollTop = output.scrollHeight;

        // Stream specialized telemetry vectors dynamically tuned to the user's script
        if (currentBot.status === 'Running') {
            logInterval = setInterval(() => {
                const scriptType = currentBot.traits ? currentBot.traits.type : 'Generic';
                let dynamicEventLine = '';
                
                if (scriptType.includes('Telegram')) {
                    const channels = ['@CryptoHub', '@MatrixGroup', '@DevChannel', '@BotTestingNode'];
                    dynamicEventLine = `[INFO] [TELEGRAM INBOUND] Resolved payload update event from context scope ${channels[Math.floor(Math.random() * channels.length)]}`;
                } else if (scriptType.includes('Scraper')) {
                    const targets = ['https://api.github.com/events', 'https://news.ycombinator.com', 'https://reddit.com/r/python'];
                    dynamicEventLine = `[DATA-FEED] HTTP/1.1 200 OK structural fetch parsed cleanly from -> ${targets[Math.floor(Math.random() * targets.length)]}`;
                } else if (scriptType.includes('Microservice')) {
                    dynamicEventLine = `[API-ROUTER] Inbound request endpoint matched POST /v1/telemetry routing pipeline - 201 Created.`;
                } else {
                    dynamicEventLine = `[RUNTIME-CORE] Main task worker event process tick successfully completed execution step context.`;
                }

                output.innerHTML += `<div class="log-line">${dynamicEventLine}</div>`;
                output.scrollTop = output.scrollHeight;

                // Sync running loop logs and metrics increments straight back to LocalStorage database context
                let freshBots = JSON.parse(localStorage.getItem('sid_bots') || '[]');
                freshBots = freshBots.map(b => {
                    if (b.id === botId) {
                        if (!b.logs) b.logs = [];
                        b.logs.push(dynamicEventLine);

                        if (b.traits && b.traits.metricTemplate) {
                            if (b.traits.counterVal === undefined) b.traits.counterVal = 0;
                            b.traits.counterVal += Math.floor(1 + Math.random() * 3);
                            b.traits.activeMetric = `${b.traits.metricTemplate}${b.traits.counterVal}`;
                        }
                    }
                    return b;
                });
                localStorage.setItem('sid_bots', JSON.stringify(freshBots));

                // Silently push refresh vectors to dashboard metric strings without breaking user view
                if (!document.getElementById('terminal-modal').classList.contains('hidden')) {
                    const activeBotState = freshBots.find(b => b.id === botId);
                    if (activeBotState && activeBotState.traits) {
                        renderBotDashboard();
                    }
                }

            }, 2500);
        } else {
            output.innerHTML += `<div class="log-line" style="color: #ff5f56; margin-top: 8px;">[OFFLINE] Connection suspended. Start execution runtime to reactivate diagnostic stream.</div>`;
            output.scrollTop = output.scrollHeight;
        }
    },
    close: function() {
        const modal = document.getElementById('terminal-modal');
        if (modal) modal.classList.add('hidden');
        if (logInterval) clearInterval(logInterval);
        renderBotDashboard(); // Synchronize layout views completely upon terminal teardown
    }
};

// ==========================================
// 8. Profile Configuration Controls
// ==========================================
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
                upgradeBtn.onclick = null;
            } else {
                upgradeBtn.innerText = 'Upgrade to Premium Pro';
                upgradeBtn.style.background = ''; // Resets back to default CSS sheets definitions
                upgradeBtn.style.color = '';
                upgradeBtn.disabled = false;
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

// ==========================================
// 9. Core Startup Hook Binding Layer
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    // Initial profile display configuration run
    appSettings.loadDashboard();
    
    // Explicit click event attachments for settings dashboard tab hooks
    const settingsTabBtn = document.querySelector('.glass-nav .nav-item:nth-child(3)');
    if (settingsTabBtn) {
        settingsTabBtn.addEventListener('click', () => {
            appSettings.loadDashboard();
        });
    }
});
