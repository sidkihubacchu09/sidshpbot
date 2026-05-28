<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SID HOSTING — Next-Gen Userbot Node</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>

    <div class="video-bg-container">
        <video id="bg-video" autoplay loop muted playsinline>
            <source src="https://cdn.pixabay.com/video/2020/05/25/40131-424785461_large.mp4" type="video/mp4">
        </video>
        <div class="video-overlay"></div>
    </div>

    <div id="toast-container" class="toast-container"></div>

    <div class="app-container" id="main-app">

        <div id="view-deploy" class="view-section active">
            
            <div class="glass-panel" id="step1-script">
                <div class="panel-header">
                    <h2 class="gradient-text">Cloud Deployment Engine</h2>
                    <span class="badge premium-badge">Node v4.1</span>
                </div>
                <p class="status-text">Enter your phone number connected to Telegram and write or upload your specialized userbot script.</p>
                
                <div class="input-group">
                    <label class="field-label">Telegram Phone Number</label>
                    <input type="tel" id="phoneInput" class="glass-input" placeholder="e.g., +1234567890" autocomplete="off">
                </div>
                
                <div class="code-editor-wrapper">
                    <div class="editor-header">
                        <div class="window-dots">
                            <span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span>
                        </div>
                        <span class="filename" id="filename-display">userbot_main.py</span>
                    </div>
                    <textarea id="scriptInput" spellcheck="false" placeholder="from telethon import TelegramClient, events&#10;&#10;# Your custom Telethon handler logic goes here..."></textarea>
                </div>

                <div class="btn-group">
                    <input type="file" id="fileUpload" accept=".py,.txt" style="display: none;" onchange="deployFlow.handleFileUpload(event)">
                    <button class="secondary-btn btn-animate" onclick="document.getElementById('fileUpload').click()">
                        <span>📤 Upload Script</span>
                    </button>
                    <button class="primary-btn btn-animate" id="btn-deploy" onclick="deployFlow.nextToOTP()">
                        <span class="btn-text">Connect Cloud Node</span>
                        <div class="spinner"></div>
                    </button>
                </div>
            </div>

            <div class="glass-panel hidden" id="step2-otp">
                <div class="panel-header">
                    <h2 class="gradient-text">Verify Node Handshake</h2>
                </div>
                <p class="status-text target-phone" id="otp-phone-display">A 5-digit verification code has been dispatched to your active Telegram application.</p>
                
                <div class="input-group text-center">
                    <label class="field-label">Telegram Login Code</label>
                    <input type="number" id="otpInput" class="glass-input text-center letters-spaced" placeholder="• • • • •" autocomplete="off">
                </div>
                
                <button class="primary-btn btn-animate" id="btn-otp" onclick="deployFlow.nextToPassword()">
                    <span class="btn-text">Verify Handshake Code</span>
                    <div class="spinner"></div>
                </button>
                <button class="secondary-btn btn-animate mt-12" onclick="deployFlow.goBack('step2-otp', 'step1-script')">Abort & Go Back</button>
            </div>

            <div class="glass-panel hidden" id="step3-password">
                <div class="panel-header">
                    <h2 class="gradient-text">Two-Step Verification</h2>
                </div>
                <p class="status-text">Your Telegram account requires a Cloud Password (2FA) to safely sign and encrypt the session.</p>
                
                <div class="input-group">
                    <label class="field-label">Telegram Cloud Password</label>
                    <input type="password" id="passwordInput" class="glass-input text-center" placeholder="••••••••••••">
                </div>
                
                <button class="primary-btn btn-animate" id="btn-pass" onclick="deployFlow.finalize()">
                    <span class="btn-text">Unlock Session & Deploy</span>
                    <div class="spinner"></div>
                </button>
                <button class="secondary-btn btn-animate mt-12" onclick="deployFlow.goBack('step3-password', 'step2-otp')">Back to OTP</button>
            </div>

            <div class="glass-panel hidden text-center" id="step4-success">
                <div class="success-ring"><span class="success-check">✓</span></div>
                <h2 class="gradient-glow-text">Deployment Successful</h2>
                <p class="status-text mt-12">Your standalone userbot script is fully securely compiled, signed, and running inside an isolated cloud container sandbox.</p>
                
                <button class="primary-btn btn-animate mt-20" onclick="nav.switchTab('view-files', document.querySelector('.nav-item:nth-child(2)'))">
                    Open Process Dashboard
                </button>
                <button class="secondary-btn btn-animate mt-12" onclick="deployFlow.reset()">
                    Deploy Secondary Instance
                </button>
            </div>
        </div>

        <div id="view-files" class="view-section hidden">
            <div class="glass-panel">
                <div class="panel-header">
                    <h2>Managed Grid Matrix</h2>
                    <span class="badge active-badge" id="bot-count-badge">🟢 1 / 2 Threads Online</span>
                </div>
                <p class="status-text">Realtime management system for your active background userbot workflows.</p>
                
                <div id="bots-list-container">
                    <div class="file-item stagger-1" id="bot-auto_reply">
                        <div class="file-info-header">
                            <div>
                                <div class="file-name">auto_reply.py</div>
                                <div class="file-status">Container Active • Uptime: <span class="timer">04h 12m</span> • Allocated: 14.2MB RAM</div>
                            </div>
                            <span class="status-dot green pulse">●</span>
                        </div>
                        <div class="file-actions">
                            <button class="action-btn text-transparent-glow" onclick="terminal.open('auto_reply.py')">📝 Terminal Logs</button>
                            <button class="action-btn text-transparent-glow" onclick="botControl.restart('auto_reply')">🔄 Restart Thread</button>
                            <button class="action-btn danger text-transparent-glow" onclick="botControl.stop('auto_reply')">⏹ Terminate</button>
                        </div>
                    </div>

                    <div class="file-item stagger-2 process-stopped" id="bot-scraper_bot">
                        <div class="file-info-header">
                            <div>
                                <div class="file-name text-muted-name">scraper_bot.py</div>
                                <div class="file-status">Process Interrupted • 0.0MB RAM</div>
                            </div>
                            <span class="status-dot red">●</span>
                        </div>
                        <div class="file-actions">
                            <button class="action-btn text-transparent-glow" onclick="terminal.open('scraper_bot.py', true)">📝 Historical Logs</button>
                            <button class="action-btn success-btn text-transparent-glow" onclick="botControl.start('scraper_bot')">▶ Initialize Node</button>
                            <button class="action-btn danger text-transparent-glow" onclick="botControl.delete('scraper_bot')">🗑 Wipe Storage</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div id="terminal-modal" class="modal-overlay hidden">
            <div class="terminal-container">
                <div class="terminal-header">
                    <div class="terminal-title">
                        <span class="dot red" onclick="terminal.close()"></span>
                        <span class="dot yellow"></span>
                        <span class="dot green"></span>
                        <span id="terminal-bot-name">stdout_stream@cloud_node</span>
                    </div>
                    <span class="close-btn" onclick="terminal.close()">✖</span>
                </div>
                <div class="terminal-body" id="terminal-output"></div>
            </div>
        </div>

        <div id="view-settings" class="view-section hidden">
            <div class="glass-panel stagger-1">
                <div class="panel-header"><h2>Account Configuration</h2></div>
                <div class="account-card-gradient">
                    <div class="account-row">
                        <span class="acc-label">Tier Status:</span>
                        <span class="acc-val premium-tier-text">Standard (Free Tier)</span>
                    </div>
                    <div class="account-row">
                        <span class="acc-label">Node Credits:</span>
                        <span class="acc-val balance-text">$0.00 USD</span>
                    </div>
                    <button class="primary-btn premium-btn btn-animate mt-12">
                        💎 Purchase Enterprise Premium Node
                    </button>
                </div>
            </div>

            <div class="glass-panel stagger-2 mt-20">
                <div class="panel-header"><h2>UI Aesthetics</h2></div>
                <div class="input-group">
                    <label class="field-label">Background Video Asset URL</label>
                    <input type="text" id="video-url-input" class="glass-input" placeholder="https://domain.com/video.mp4" value="https://cdn.pixabay.com/video/2020/05/25/40131-424785461_large.mp4">
                    <button class="secondary-btn btn-animate" onclick="uiEngine.updateBackgroundFromSettings()">Update Fluid Stream Asset</button>
                </div>
            </div>
        </div>

        <div id="view-admin" class="view-section hidden">
            <div class="glass-panel text-center" id="admin-login-panel">
                <div class="panel-header justify-center">
                    <h2 class="gradient-text">Admin Gatekeeper</h2>
                </div>
                <p class="status-text">Root access validation mandatory. Session attempts are log-monitored.</p>
                <input type="password" id="adminPassInput" class="glass-input text-center" placeholder="Enter System Token Key">
                <button class="primary-btn btn-animate" id="btn-admin-login" onclick="adminDashboard.verifyPassword()">
                    <span class="btn-text">Authenticate Core Token</span>
                    <div class="spinner"></div>
                </button>
            </div>

            <div class="glass-panel hidden" id="admin-dash-panel">
                <div class="panel-header">
                    <h2 class="gradient-text">Master Server Matrix</h2>
                    <span class="badge active-badge" id="global-server-badge">● Engine Online</span>
                </div>
                <p class="status-text" id="server-status-text"><span class="pulse status-dot green">●</span>Primary Node Cluster operational (Cluster Latency: 12ms)</p>
                
                <div class="admin-stats-grid">
                    <div class="stat-card">
                        <div class="stat-value" id="stat-active-bots">14</div>
                        <div class="stat-label">Active Processes</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="stat-cpu-load">89%</div>
                        <div class="stat-label">CPU Core Stress</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="stat-total-users">1,204</div>
                        <div class="stat-label">Registered Accounts</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value neon-green" id="stat-payments">$345.00</div>
                        <div class="stat-label">Gross Intake (24h)</div>
                    </div>
                </div>

                <div class="admin-section-block">
                    <p class="block-title">Master Process Hypervisor Power State</p>
                    <div class="power-btn-flex">
                        <button class="action-btn success-btn text-transparent-glow" onclick="adminDashboard.toggleServerPower(true)">▶ Power ON Nodes</button>
                        <button class="action-btn danger text-transparent-glow" onclick="adminDashboard.toggleServerPower(false)">⏹ Kill Hypervisor Threads</button>
                    </div>
                </div>

                <div class="admin-section-block mt-16">
                    <p class="block-title">Override Global Live Broadcast Background</p>
                    <input type="text" id="admin-video-url-input" class="glass-input" placeholder="https://cdn.example.com/asset.mp4" value="https://cdn.pixabay.com/video/2020/05/25/40131-424785461_large.mp4">
                    <button class="secondary-btn btn-animate" onclick="adminDashboard.updateGlobalBackground()">
                        🎬 Broadcast Global Fluid Video Asset
                    </button>
                </div>

                <div class="admin-section-block mt-16">
                    <p class="block-title">Premium Nodes Registry (Live Database View)</p>
                    <div class="premium-users-list">
                        <div class="user-row"><span>@alpha_dev (Premium Node #1)</span><span class="status-text-green">Active</span></div>
                        <div class="user-row"><span>@cryptoking (Premium Node #2)</span><span class="status-text-green">Active</span></div>
                        <div class="user-row"><span>@sid999_vip (Premium Master)</span><span class="status-text-gold">Lifetime Premium</span></div>
                        <div class="user-row text-muted-name"><span>@tester_account (Free Sandbox)</span><span class="text-muted-name">Unpaid Standard</span></div>
                    </div>
                </div>

                <button class="secondary-btn admin-logout-btn btn-animate mt-20" onclick="adminDashboard.logout()">Wipe Access Tokens & Logout</button>
            </div>
        </div>

    </div>

    <nav class="glass-nav">
        <div class="nav-item active" onclick="nav.switchTab('view-deploy', this)">
            <span class="nav-icon">☁️</span><span class="nav-label">Deploy Node</span>
        </div>
        <div class="nav-item" onclick="nav.switchTab('view-files', this)">
            <span class="nav-icon">🤖</span><span class="nav-label">My Bots</span>
        </div>
        <div class="nav-item" onclick="nav.switchTab('view-settings', this)">
            <span class="nav-icon">⚙️</span><span class="nav-label">Settings</span>
        </div>
        <div class="nav-item" onclick="nav.switchTab('view-admin', this)">
            <span class="nav-icon">🛡️</span><span class="nav-label">Admin Core</span>
        </div>
    </nav>

    <script src="js/script.js"></script>
</body>
</html>
