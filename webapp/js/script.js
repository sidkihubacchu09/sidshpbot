// ==========================================================================
//  1. BOTTOM NAVIGATION LOGIC
// ==========================================================================
const nav = {
    switchTab: (targetId, clickedElement) => {
        // Hide all views
        document.querySelectorAll('.view-section').forEach(el => {
            el.classList.add('hidden');
            el.classList.remove('active');
        });
        
        // Remove active state from all nav icons
        document.querySelectorAll('.nav-item').forEach(el => {
            el.classList.remove('active');
        });

        // Show the targeted view
        const targetView = document.getElementById(targetId);
        targetView.classList.remove('hidden');
        
        // Small delay to ensure CSS animation triggers properly
        setTimeout(() => {
            targetView.classList.add('active');
        }, 10);

        // Highlight the clicked nav icon
        clickedElement.classList.add('active');
    }
};

// ==========================================================================
//  2. DEPLOYMENT WIZARD LOGIC (Visual State Only)
// ==========================================================================
const deployFlow = {
    handleFileUpload: (event) => {
        const file = event.target.files[0];
        if (file) {
            document.getElementById('filename-display').innerText = file.name;
        }
    },
    
    // UI progression methods
    nextToOTP: () => {
        document.getElementById('step1-script').classList.add('hidden');
        document.getElementById('step2-otp').classList.remove('hidden');
    },
    
    nextToPassword: () => {
        document.getElementById('step2-otp').classList.add('hidden');
        document.getElementById('step3-password').classList.remove('hidden');
    },
    
    finalize: () => {
        document.getElementById('step3-password').classList.add('hidden');
        document.getElementById('step4-success').classList.remove('hidden');
    },
    
    goBack: (currentStepId, previousStepId) => {
        document.getElementById(currentStepId).classList.add('hidden');
        document.getElementById(previousStepId).classList.remove('hidden');
    },
    
    reset: () => {
        // Clear inputs visually
        document.getElementById('phoneInput').value = '';
        document.getElementById('otpInput').value = '';
        document.getElementById('passwordInput').value = '';
        
        // Return to first screen
        document.getElementById('step4-success').classList.add('hidden');
        document.getElementById('step1-script').classList.remove('hidden');
    }
};

// ==========================================================================
//  3. TERMINAL MODAL LOGIC
// ==========================================================================
const terminal = {
    open: (botName) => {
        document.getElementById('terminal-bot-name').innerText = botName;
        document.getElementById('terminal-modal').classList.remove('hidden');
        
        // Inject a mock connection log
        const output = document.getElementById('terminal-output');
        output.innerHTML = `<div class="log-line log-info">[SYSTEM] Initializing connection to ${botName}...</div>
                            <div class="log-line" style="animation-delay: 0.5s; opacity: 0;">[OK] Node environment loaded.</div>`;
    },
    
    close: () => {
        document.getElementById('terminal-modal').classList.add('hidden');
    }
};

// ==========================================================================
//  4. ADMIN MOCK LOGIN LOGIC
// ==========================================================================
const adminFlow = {
    login: () => {
        document.getElementById('admin-login-panel').classList.add('hidden');
        document.getElementById('admin-dash-panel').classList.remove('hidden');
    },
    
    logout: () => {
        document.getElementById('adminPassInput').value = '';
        document.getElementById('admin-dash-panel').classList.add('hidden');
        document.getElementById('admin-login-panel').classList.remove('hidden');
    }
};

// ==========================================================================
//  5. SETTINGS LOGIC
// ==========================================================================
const appSettings = {
    updateVideo: () => {
        const newUrl = document.getElementById('video-url-input').value;
        const videoElement = document.getElementById('bg-video');
        
        if (newUrl) {
            videoElement.src = newUrl;
            videoElement.play().catch(e => console.log("Autoplay blocked by browser."));
        }
    }
};
