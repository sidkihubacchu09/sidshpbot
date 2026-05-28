// --- Navigation Controller ---
const nav = {
    switchTab: (tabId, element) => {
        // Hide all views
        document.querySelectorAll('.view-section').forEach(view => view.classList.add('hidden'));
        document.getElementById(tabId).classList.remove('hidden');
        
        // Update active nav styling
        document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
        if(element) element.classList.add('active');
    }
};

// --- Deployment Flow (Userbot Logic) ---
const deployFlow = {
    handleFileUpload: (event) => {
        const file = event.target.files[0];
        if (file) {
            document.getElementById('filename-display').innerText = file.name;
        }
    },
    
    setLoading: (btnId, isLoading) => {
        const btn = document.getElementById(btnId);
        if (isLoading) btn.classList.add('loading');
        else btn.classList.remove('loading');
    },

    transitionPanel: (hideId, showId) => {
        document.getElementById(hideId).classList.add('hidden');
        document.getElementById(showId).classList.remove('hidden');
    },

    goBack: (currentId, previousId) => {
        deployFlow.transitionPanel(currentId, previousId);
    },

    // Step 1 -> Step 2 (Phone to OTP)
    nextToOTP: () => {
        const phone = document.getElementById('phoneInput').value;
        if (!phone) {
            alert("Please enter your Telegram phone number.");
            return;
        }
        
        deployFlow.setLoading('btn-deploy', true);
        
        // Simulate API call to backend to request Telegram OTP
        setTimeout(() => {
            deployFlow.setLoading('btn-deploy', false);
            document.getElementById('otp-phone-display').innerText = `We sent a Telegram login code to ${phone}.`;
            deployFlow.transitionPanel('step1-script', 'step2-otp');
        }, 1500);
    },

    // Step 2 -> Step 3 (OTP to 2FA)
    nextToPassword: () => {
        const otp = document.getElementById('otpInput').value;
        if (!otp) return alert("Please enter the OTP.");
        
        deployFlow.setLoading('btn-otp', true);
        
        // Simulate API call to verify OTP and request 2FA
        setTimeout(() => {
            deployFlow.setLoading('btn-otp', false);
            deployFlow.transitionPanel('step2-otp', 'step3-password');
        }, 1500);
    },

    // Step 3 -> Step 4 (2FA to Success)
    finalize: () => {
        const password = document.getElementById('passwordInput').value;
        deployFlow.setLoading('btn-pass', true);
        
        // Simulate finalizing Telethon session
        setTimeout(() => {
            deployFlow.setLoading('btn-pass', false);
            deployFlow.transitionPanel('step3-password', 'step4-success');
        }, 2000);
    },

    // Reset Flow
    reset: () => {
        document.getElementById('phoneInput').value = '';
        document.getElementById('otpInput').value = '';
        document.getElementById('passwordInput').value = '';
        deployFlow.transitionPanel('step4-success', 'step1-script');
    }
};

// --- Admin Controls ---
const adminFlow = {
    verify: () => {
        const pass = document.getElementById('adminPassInput').value;
        const btn = document.getElementById('btn-admin-login');
        
        btn.classList.add('loading');
        
        setTimeout(() => {
            btn.classList.remove('loading');
            if (pass === 'sid999') {
                document.getElementById('admin-login-panel').classList.add('hidden');
                document.getElementById('admin-dash-panel').classList.remove('hidden');
                document.getElementById('adminPassInput').value = '';
            } else {
                alert('Access Denied. Incorrect Password.');
            }
        }, 1000);
    },

    logout: () => {
        document.getElementById('admin-dash-panel').classList.add('hidden');
        document.getElementById('admin-login-panel').classList.remove('hidden');
    },

    togglePower: (turnOn) => {
        const statusText = document.getElementById('server-status-text');
        if (turnOn) {
            statusText.style.color = '#27c93f';
            statusText.innerHTML = '<span class="pulse status-dot green" style="display:inline-block; font-size:0.8rem; margin-right:5px;">●</span>Node is online (Ping: 12ms)';
        } else {
            statusText.style.color = '#ff5f56';
            statusText.innerHTML = '<span class="status-dot red" style="display:inline-block; font-size:0.8rem; margin-right:5px;">●</span>Node is offline';
        }
    },

    updateVideo: () => {
        const url = document.getElementById('admin-video-url').value;
        const video = document.getElementById('bg-video');
        if (video && url) {
            video.src = url;
            video.load();
            video.play().catch(e => console.log("Video updated but autoplay blocked."));
        }
    }
};
