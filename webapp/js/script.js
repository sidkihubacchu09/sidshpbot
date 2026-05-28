// Initialize Telegram Web App API
const tg = window.Telegram.WebApp;

// Expand WebApp to full height on open
tg.expand();

// Let TG handle theme colors (Optional, as our CSS overrides mostly with glass theme)
tg.ready();

// Utility for providing Haptic Feedback (Phone Vibration)
const haptic = {
    tap: () => tg.HapticFeedback.impactOccurred('light'),
    success: () => tg.HapticFeedback.notificationOccurred('success'),
    error: () => tg.HapticFeedback.notificationOccurred('error')
};

// --- Navigation Controller ---
const nav = {
    switchTab: function(targetId) {
        haptic.tap();
        
        // Update Bottom Nav UI
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if(item.dataset.target === targetId) {
                item.classList.add('active');
            }
        });

        // Hide all views, show target view
        document.querySelectorAll('.view-section').forEach(view => {
            view.classList.remove('active');
            view.classList.add('hidden');
        });

        document.getElementById(`view-${targetId}`).classList.remove('hidden');
        // Small delay to allow display:block to apply before animating opacity
        setTimeout(() => {
            document.getElementById(`view-${targetId}`).classList.add('active');
        }, 10);
    }
};

// --- Terminal Simulator ---
const terminal = {
    el: document.getElementById('terminal-output'),
    
    log: function(msg, type="info") {
        const line = document.createElement('div');
        line.className = `log-line ${type}`;
        
        // Add timestamp
        const time = new Date().toLocaleTimeString('en-US', {hour12: false, hour: "numeric", minute: "numeric", second: "numeric"});
        line.textContent = `[${time}] ${msg}`;
        
        this.el.appendChild(line);
        this.el.scrollTop = this.el.scrollHeight; // Auto-scroll
    }
};

// --- Deployment Flow Controller ---
const deployFlow = {
    
    setLoading: function(btnId, isLoading) {
        const btn = document.getElementById(btnId);
        const text = btn.querySelector('.btn-text');
        const spin = btn.querySelector('.spinner');
        
        if(isLoading) {
            btn.disabled = true;
            text.style.display = 'none';
            spin.style.display = 'block';
        } else {
            btn.disabled = false;
            text.style.display = 'block';
            spin.style.display = 'none';
        }
    },

    switchPanel: function(hideId, showId) {
        document.getElementById(hideId).classList.add('hidden');
        document.getElementById(showId).classList.remove('hidden');
    },

    goBack: function(currentId, previousId) {
        haptic.tap();
        this.switchPanel(currentId, previousId);
    },

    // Step 1 -> 2
    nextToOTP: function() {
        const script = document.getElementById('scriptInput').value;
        if(script.trim() === "") {
            haptic.error();
            tg.showAlert("Script cannot be empty!");
            return;
        }

        haptic.tap();
        this.setLoading('btn-deploy', true);
        terminal.log("Initializing secure container...", "system");

        // Simulate API call to backend to request OTP
        setTimeout(() => {
            this.setLoading('btn-deploy', false);
            this.switchPanel('step1-script', 'step2-otp');
            terminal.log("Sent OTP request to Telegram servers.", "info");
        }, 1500);
    },

    // Step 2 -> 3
    nextToPassword: function() {
        const otp = document.getElementById('otpInput').value;
        if(otp.length < 5) {
            haptic.error();
            tg.showAlert("Please enter a valid 5-digit code.");
            return;
        }

        haptic.tap();
        this.setLoading('btn-otp', true);
        terminal.log("Verifying authorization code...", "system");

        // Simulate API call to submit OTP
        setTimeout(() => {
            this.setLoading('btn-otp', false);
            this.switchPanel('step2-otp', 'step3-password');
            terminal.log("2FA Challenge required. Waiting for password...", "info");
        }, 1500);
    },

    // Step 3 -> 4 (Final)
    finalize: function() {
        const pass = document.getElementById('passwordInput').value;
        if(!pass.trim()) {
            haptic.error();
            tg.showAlert("Cloud password is required.");
            return;
        }

        haptic.tap();
        this.setLoading('btn-pass', true);
        terminal.log("Decrypting session with Cloud Password...", "system");

        // Simulate API call to finish login and boot bot
        setTimeout(() => {
            this.setLoading('btn-pass', false);
            this.switchPanel('step3-password', 'step4-success');
            
            haptic.success();
            terminal.log("Session verified successfully!", "success");
            terminal.log("Booting UserBot Core...", "info");
            
            setTimeout(() => {
                terminal.log("UserBot is now ONLINE and listening to events.", "success");
            }, 1000);

        }, 2000);
    }
};
