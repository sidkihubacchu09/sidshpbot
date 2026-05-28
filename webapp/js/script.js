/**
 * SID HOSTING APPLICATION HUB INTERFACE
 * Handles active user states, API connection callbacks, background modifications, and dynamic web telemetry.
 */

class AppEngine {
    constructor() {
        this.apiBase = window.location.origin;
        this.userId = 12345678; // Fallback demo tracking parameters
        this.currentUploadedScript = null;

        // Initialize connection mapping safely with Telegram WebApp ecosystem
        if (window.Telegram && window.Telegram.WebApp) {
            window.Telegram.WebApp.ready();
            window.Telegram.WebApp.expand();
            if (window.Telegram.WebApp.initDataUnsafe?.user) {
                this.userId = window.Telegram.WebApp.initDataUnsafe.user.id;
            }
        }
    }

    init() {
        console.log("Initializing Dashboard Script Interface Core...");
        this.synchronizeTelemetry();
        // Periodically pull live instance logging buffers
        setInterval(() => this.synchronizeTelemetry(), 5000);
    }

    // Handle view section swaps via navigation dock
    navigateView(element, viewId) {
        document.querySelectorAll('.dock-item').forEach(item => item.classList.remove('active'));
        document.querySelectorAll('.view-section').forEach(view => view.classList.remove('active'));
        
        element.classList.add('active');
        document.getElementById(viewId).classList.add('active');
    }

    switchPanel(currentId, targetId) {
        document.getElementById(currentId).classList.add('hidden');
        document.getElementById(targetId).classList.remove('hidden');
    }

    handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        this.currentUploadedScript = file.name;
        document.getElementById('filename-display').innerHTML = `<i class="fa-solid fa-file-arrow-up text-green"></i> ${file.name}`;
        
        const reader = new FileReader();
        reader.onload = (e) => {
            document.getElementById('scriptInput').value = e.target.result;
        };
        reader.readAsText(file);
    }

    // Step 1: Submit Code and initialization criteria to Python Async Worker
    initiateConnection() {
        const phone = document.getElementById('phoneInput').value;
        const apiId = document.getElementById('apiIdInput').value;
        const apiHash = document.getElementById('apiHashInput').value;
        const scriptCode = document.getElementById('scriptInput').value;

        if (!phone || !apiId || !apiHash || !scriptCode) {
            alert("⚠️ Matrix Configuration Error: Ensure Phone, credentials, and script assets are loaded.");
            return;
        }

        this.setButtonLoading('btn-deploy', true);

        fetch(`${this.apiBase}/api/deploy/initiate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: this.userId,
                phone: phone,
                api_id: apiId,
                api_hash: apiHash,
                script: scriptCode
            })
        })
        .then(res => res.json())
        .then(data => {
            this.setButtonLoading('btn-deploy', false);
            if (data.status === "otp_required") {
                document.getElementById('otp-phone-display').innerText = `Dynamic session authorization node dispatched to ${phone}`;
                this.switchPanel('step1-script', 'step2-otp');
            } else {
                alert(`❌ Engine rejection callback: ${data.message}`);
            }
        })
        .catch(err => {
            this.setButtonLoading('btn-deploy', false);
            alert("❌ System loop failure tracking connection.");
        });
    }

    // Step 2: Submit Received Session Code Token
    verifyOTP() {
        const otpCode = document.getElementById('otpInput').value;
        if (!otpCode) return alert("Please specify the verification token code.");

        this.setButtonLoading('btn-otp', true);

        fetch(`${this.apiBase}/api/deploy/verify-otp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: this.userId, otp: otpCode })
        })
        .then(res => res.json())
        .then(data => {
            this.setButtonLoading('btn-otp', false);
            if (data.status === "password_required") {
                this.switchPanel('step2-otp', 'step3-password');
            } else if (data.status === "success") {
                alert("🚀 Secure instance successfully compiled! Active cluster allocation processing.");
                window.location.reload();
            } else {
                alert(`❌ Token error: ${data.message}`);
            }
        });
    }

    // Step 3: Authenticate Cloud Password
    verifyPassword() {
        const cloudPassword = document.getElementById('passwordInput').value;
        if (!cloudPassword) return alert("2-Step Verification String Required.");

        this.setButtonLoading('btn-password', true);

        fetch(`${this.apiBase}/api/deploy/verify-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: this.userId, password: cloudPassword })
        })
        .then(res => res.json())
        .then(data => {
            this.setButtonLoading('btn-password', false);
            if (data.status === "success") {
                alert("🚀 Secure instance initialized. Pipeline running!");
                this.switchPanel('step3-password', 'step1-script');
            } else {
                alert(`❌ Execution runtime fault: ${data.message}`);
            }
        });
    }

    // Administrative Wallpaper Engine Management Function
    applyBackgroundVideo() {
        const videoUrl = document.getElementById('adminVideoInput').value;
        if (!videoUrl) return alert("Provide a target background streaming link.");

        fetch(`${this.apiBase}/api/admin/set-background`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: this.userId, video_url: videoUrl })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const videoElement = document.getElementById('bg-video');
                videoElement.src = videoUrl;
                videoElement.load();
                videoElement.play().catch(e => console.log("Wallpaper pipeline hot reloaded."));
                alert("🎯 Application backdrop wallpaper updated across environments.");
            } else {
                alert("❌ Administrative request access denied.");
            }
        });
    }

    synchronizeTelemetry() {
        fetch(`${this.apiBase}/api/telemetry?user_id=${this.userId}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById('dash-status').innerText = data.runtime_status || "Offline";
            document.getElementById('dash-slots').innerText = `${data.file_count || 0} / ${data.limit || 10} Clusters`;
            document.getElementById('dash-role').innerText = data.role_title || "Standard Tier";
            
            if (data.bg_video) {
                const videoElement = document.getElementById('bg-video');
                if (!videoElement.src.includes(data.bg_video)) {
                    videoElement.src = data.bg_video;
                }
            }

            if (data.logs) {
                document.getElementById('terminal-logs').innerHTML = data.logs.join("<br>");
            }
        }).catch(() => {});
    }

    setButtonLoading(btnId, isLoading) {
        const btn = document.getElementById(btnId);
        if (!btn) return;
        if (isLoading) {
            btn.disabled = true;
            btn.style.opacity = '0.6';
        } else {
            btn.disabled = false;
            btn.style.opacity = '1';
        }
    }

    triggerGlobalLock() { alert("🔒 Main Cluster Ecosystem lockdown initiated via Admin Token."); }
    clearOrphanProcesses() { alert("🧹 Closed process transaction threads cleared."); }
}

const appEngine = new AppEngine();
document.addEventListener('DOMContentLoaded', () => appEngine.init());
