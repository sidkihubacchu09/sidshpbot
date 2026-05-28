// ==========================================================================
// Utility: Simulate delays
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// --- Navigation Controller ---
const nav = {
    switchTab(targetId, element) {
        document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
        element.classList.add('active');

        document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
        document.getElementById(targetId).classList.add('active');
    }
};

// --- Deployment Controller ---
const deployFlow = {
    handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        document.getElementById('filename-display').innerText = file.name;
        const reader = new FileReader();
        reader.onload = (e) => {
            document.getElementById('scriptInput').value = e.target.result;
        };
        reader.readAsText(file);
    },

    async nextToOTP() {
        const phone = document.getElementById('phoneInput').value;
        const script = document.getElementById('scriptInput').value;
        
        if(!phone || !script) {
            alert("Please enter a phone number and a script.");
            return;
        }

        const btn = document.getElementById('btn-deploy');
        btn.classList.add('btn-loading');
        await sleep(1500); 
        btn.classList.remove('btn-loading');

        document.getElementById('otp-phone-display').innerText = `Code sent to ${phone}`;
        this.switchStep('step1-script', 'step2-otp');
    },

    async nextToPassword() {
        const otp = document.getElementById('otpInput').value;
        if(otp.length < 5) { alert("Please enter a valid OTP."); return; }

        const btn = document.getElementById('btn-otp');
        btn.classList.add('btn-loading');
        await sleep(1200); 
        btn.classList.remove('btn-loading');

        this.switchStep('step2-otp', 'step3-password');
    },

    async finalize() {
        const pass = document.getElementById('passwordInput').value;
        if(!pass) { alert("Password required for 2FA."); return; }

        const btn = document.getElementById('btn-pass');
        btn.classList.add('btn-loading');
        await sleep(2000); 
        btn.classList.remove('btn-loading');

        this.switchStep('step3-password', 'step4-success');
    },

    switchStep(hideId, showId) {
        document.getElementById(hideId).classList.add('hidden');
        document.getElementById(showId).classList.remove('hidden');
    },
    goBack(currentId, targetId) { this.switchStep(currentId, targetId); },
    reset() {
        document.getElementById('phoneInput').value = "";
        document.getElementById('scriptInput').value = "";
        document.getElementById('otpInput').value = "";
        document.getElementById('passwordInput').value = "";
        document.getElementById('filename-display').innerText = "main.py";
        this.switchStep('step4-success', 'step1-script');
    }
};

// --- Terminal / Live Working Process Controller ---
const terminal = {
    modal: document.getElementById('terminal-modal'),
    output: document.getElementById('terminal-output'),
    title: document.getElementById('terminal-bot-name'),
    isTyping: false,
    intervalId: null,

    open(botName, isStopped = false) {
        this.title.innerText = `~/cloud/bots/${botName}`;
        this.output.innerHTML = ''; 
        this.modal.classList.remove('hidden');
        this.isTyping = true;

        if(isStopped) {
            this.addLog(`Process ${botName} is currently offline.`, 'log-err');
            this.addLog("Click 'Start' in the dashboard to initialize.", 'log-warn');
            return;
        }

        // Simulate active bot booting up and working
        this.simulateProcess(botName);
    },

    close() {
        this.modal.classList.add('hidden');
        this.isTyping = false;
        clearInterval(this.intervalId);
    },

    addLog(text, className = '') {
        const line = document.createElement('div');
        line.className = `log-line ${className}`;
        const time = new Date().toLocaleTimeString([], { hour12: false });
        line.innerHTML = `<span style="color: #666;">[${time}]</span> ${text}`;
        this.output.appendChild(line);
        this.output.scrollTop = this.output.scrollHeight;
    },

    async simulateProcess(botName) {
        this.addLog(`Initializing virtual environment for ${botName}...`, 'log-info');
        await sleep(800);
        if(!this.isTyping) return;
        
        this.addLog("Authenticating Telegram session via Telethon...");
        await sleep(1000);
        if(!this.isTyping) return;

        this.addLog("Session decrypted successfully. Connected to DC-4.", 'log-info');
        await sleep(600);
        this.addLog("Bot is now listening for events...");

        // Continuous simulated activity loop
        this.intervalId = setInterval(() => {
            const actions = [
                "Received MessageUpdate (ChatID: -100928374)",
                "<span class='log-warn'>Handling anti-spam filters... passed.</span>",
                "Processed trigger '/ping'. Replied in 0.42s",
                "<span class='log-info'>Auto-reply executed in chat User_1092.</span>",
                "Scraping new members in target group (Found 3)...",
                "Ping to API server: 14ms"
            ];
            const randomAction = actions[Math.floor(Math.random() * actions.length)];
            this.addLog(randomAction);
        }, 2500);
    }
};

// --- Settings & Admin ---
const appSettings = {
    updateVideo() {
        const url = document.getElementById('video-url-input').value;
        const videoElement = document.getElementById('bg-video');
        if(url) {
            videoElement.src = url;
            videoElement.play();
            alert("Background updated! The UI will feel incredibly smooth.");
        }
    }
};

const adminFlow = {
    async login() {
        const pass = document.getElementById('adminPassInput').value;
        const btn = document.getElementById('btn-admin-login');
        if(pass !== "admin123") { alert("Invalid Admin Credentials"); return; }
        
        btn.classList.add('btn-loading');
        await sleep(1000);
        btn.classList.remove('btn-loading');

        document.getElementById('admin-login-panel').classList.add('hidden');
        document.getElementById('admin-dash-panel').classList.remove('hidden');
        document.getElementById('adminPassInput').value = "";
    },
    logout() {
        document.getElementById('admin-dash-panel').classList.add('hidden');
        document.getElementById('admin-login-panel').classList.remove('hidden');
    }
};
