const tg = window.Telegram.WebApp;
tg.expand();

// Utility for providing Haptic Feedback
const haptic = {
    tap: () => tg.HapticFeedback.impactOccurred('light'),
    success: () => tg.HapticFeedback.notificationOccurred('success'),
    error: () => tg.HapticFeedback.notificationOccurred('error')
};

// Global App State
let IS_WEB_ENABLED = true; 

// Initial check to see if Web is enabled
window.onload = async () => {
    try {
        let res = await fetch('/api/public/status');
        let data = await res.json();
        IS_WEB_ENABLED = data.web_enabled;
        
        // Load custom video if set
        if(data.video_bg) {
            document.getElementById('bg-video').src = data.video_bg;
        }

        if (!IS_WEB_ENABLED) {
            document.getElementById('step1-script').innerHTML = `<h2 class="text-center mt-20">Maintenance</h2><p class="status-text text-center">Web deployment is currently disabled by Admin.</p>`;
        }
    } catch(e) {}
};

const nav = {
    switchTab: function(targetId) {
        haptic.tap();
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if(item.dataset.target === targetId || (targetId === 'admin-login' && item.dataset.target === 'admin')) item.classList.add('active');
        });
        document.querySelectorAll('.view-section').forEach(view => {
            view.classList.remove('active');
            setTimeout(()=> view.classList.add('hidden'), 50);
        });
        
        let targetView = document.getElementById(`view-${targetId}`);
        targetView.classList.remove('hidden');
        setTimeout(() => targetView.classList.add('active'), 60);
    }
};

// --- User Deployment Flow ---
const deployFlow = {
    sessionPhone: "", phoneCodeHash: "",
    
    setLoading: function(btnId, isLoading) {
        const btn = document.getElementById(btnId);
        if(isLoading) { btn.disabled = true; btn.querySelector('.btn-text').style.display='none'; btn.querySelector('.spinner').style.display='block'; } 
        else { btn.disabled = false; btn.querySelector('.btn-text').style.display='block'; btn.querySelector('.spinner').style.display='none'; }
    },
    switchPanel: function(hideId, showId) { document.getElementById(hideId).classList.add('hidden'); document.getElementById(showId).classList.remove('hidden'); },

    nextToOTP: async function() {
        if(!IS_WEB_ENABLED) return tg.showAlert("Web deployment disabled.");
        
        const phone = document.getElementById('phoneInput').value;
        const script = document.getElementById('scriptInput').value;
        if(!phone || !script) return tg.showAlert("Phone number and script are required.");

        haptic.tap();
        this.setLoading('btn-deploy', true);

        try {
            let res = await fetch('/api/request_code', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ phone: phone, script: script })
            });
            let data = await res.json();
            if (data.status === "success") {
                this.sessionPhone = phone;
                this.phoneCodeHash = data.phone_code_hash;
                document.getElementById('otp-phone-display').innerText = `Code sent to ${phone}`;
                this.switchPanel('step1-script', 'step2-otp');
            } else tg.showAlert("Error: " + data.message);
        } catch (err) { tg.showAlert("Network error."); }
        this.setLoading('btn-deploy', false);
    },

    nextToPassword: async function() {
        const otp = document.getElementById('otpInput').value;
        if(!otp) return tg.showAlert("Enter OTP.");

        haptic.tap();
        this.setLoading('btn-otp', true);

        try {
            let res = await fetch('/api/verify_code', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ phone: this.sessionPhone, code: otp, phone_code_hash: this.phoneCodeHash })
            });
            let data = await res.json();
            if (data.status === "success") {
                this.switchPanel('step2-otp', 'step4-success');
                haptic.success(); this.bootBot();
            } else if (data.status === "password_required") {
                this.switchPanel('step2-otp', 'step3-password');
            } else tg.showAlert("Error: " + data.message);
        } catch (err) { tg.showAlert("Network error."); }
        this.setLoading('btn-otp', false);
    },

    finalize: async function() {
        const pass = document.getElementById('passwordInput').value;
        if(!pass) return tg.showAlert("Enter password.");

        haptic.tap();
        this.setLoading('btn-pass', true);

        try {
            let res = await fetch('/api/verify_password', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ phone: this.sessionPhone, password: pass })
            });
            let data = await res.json();
            if (data.status === "success") {
                this.switchPanel('step3-password', 'step4-success');
                haptic.success(); this.bootBot();
            } else tg.showAlert("Error: " + data.message);
        } catch (err) { tg.showAlert("Network error."); }
        this.setLoading('btn-pass', false);
    },

    bootBot: async function() {
        await fetch('/api/start_bot', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ phone: this.sessionPhone }) });
    }
};

// --- Admin Flow ---
const adminFlow = {
    setLoading: function(isLoading) {
        const btn = document.getElementById('btn-admin-login');
        if(isLoading) { btn.disabled = true; btn.querySelector('.btn-text').style.display='none'; btn.querySelector('.spinner').style.display='block'; } 
        else { btn.disabled = false; btn.querySelector('.btn-text').style.display='block'; btn.querySelector('.spinner').style.display='none'; }
    },

    login: async function() {
        const pass = document.getElementById('adminPassInput').value;
        if(pass !== "sid999") { haptic.error(); return tg.showAlert("Incorrect Admin Password!"); }
        
        haptic.tap();
        this.setLoading(true);
        
        // Fetch Admin Stats
        try {
            let start = Date.now();
            let res = await fetch('/api/admin/stats', { headers: {'Authorization': 'sid999'} });
            let ping = Date.now() - start;
            let data = await res.json();
            
            document.getElementById('server-ping').innerText = `Ping: ${ping}ms`;
            document.getElementById('stat-users').innerText = data.active_users;
            document.getElementById('stat-scripts').innerText = data.running_bots;
            document.getElementById('toggle-web').checked = data.web_enabled;
            
            document.getElementById('view-admin-login').classList.add('hidden');
            document.getElementById('view-admin-dash').classList.remove('hidden');
            haptic.success();
        } catch(e) { tg.showAlert("Failed to connect to backend."); }
        this.setLoading(false);
    },

    toggleWeb: async function() {
        let isEnabled = document.getElementById('toggle-web').checked;
        await fetch('/api/admin/toggle_web', { 
            method: 'POST', headers: {'Authorization': 'sid999', 'Content-Type': 'application/json'},
            body: JSON.stringify({ state: isEnabled })
        });
        haptic.tap();
    },

    setVideoBG: async function() {
        let url = document.getElementById('video-url-input').value;
        if(!url) return;
        await fetch('/api/admin/set_bg', { 
            method: 'POST', headers: {'Authorization': 'sid999', 'Content-Type': 'application/json'},
            body: JSON.stringify({ url: url })
        });
        document.getElementById('bg-video').src = url;
        tg.showAlert("Background updated!");
        haptic.success();
    },

    fetchFiles: async function() {
        try {
            let res = await fetch('/api/admin/files', { headers: {'Authorization': 'sid999'} });
            let data = await res.json();
            let list = document.getElementById('admin-files-list');
            list.innerHTML = data.files.map(f => `<div>📄 ${f}</div>`).join('');
            list.classList.remove('hidden');
        } catch(e) { tg.showAlert("Error fetching files."); }
    }
};
