const tg = window.Telegram.WebApp;
tg.expand(); 
tg.ready();

const mainBtn = tg.MainButton;
mainBtn.color = '#00d2ff';
mainBtn.textColor = '#000000';

let currentStep = 1;

window.onload = () => {
    document.body.style.backgroundColor = tg.themeParams.bg_color || '#0f172a';
    mainBtn.setText("INITIALIZE SCRIPT");
    mainBtn.show();
    mainBtn.onClick(handleMainAction);
};

function handleMainAction() {
    tg.HapticFeedback.impactOccurred('light');

    if (currentStep === 1) processScript();
    else if (currentStep === 2) processOTP();
    else if (currentStep === 3) processPassword();
    else if (currentStep === 4) tg.close();
}

function processScript() {
    const script = document.getElementById('scriptInput').value.trim();
    if (!script) return triggerError("Please enter your bot script.");

    mainBtn.showProgress();
    mainBtn.disable();

    setTimeout(() => {
        mainBtn.hideProgress();
        mainBtn.enable();
        mainBtn.setText("VERIFY OTP");
        
        switchStep('step1-script', 'step2-otp');
        currentStep = 2;
        setTimeout(() => document.getElementById('otpInput').focus(), 400);
    }, 1500);
}

function processOTP() {
    const otp = document.getElementById('otpInput').value.trim();
    if (otp.length < 5) return triggerError("Invalid OTP. Must be at least 5 digits.");

    mainBtn.showProgress();
    mainBtn.disable();

    setTimeout(() => {
        mainBtn.hideProgress();
        mainBtn.enable();
        mainBtn.setText("START USERBOT");
        
        switchStep('step2-otp', 'step3-password');
        currentStep = 3;
        setTimeout(() => document.getElementById('passwordInput').focus(), 400);
    }, 1500);
}

function processPassword() {
    const password = document.getElementById('passwordInput').value.trim();
    if (!password) return triggerError("2FA Password is required.");

    mainBtn.showProgress();
    mainBtn.disable();

    setTimeout(() => {
        mainBtn.hideProgress();
        mainBtn.enable();
        tg.HapticFeedback.notificationOccurred('success');
        
        mainBtn.color = '#4ade80';
        mainBtn.setText("CLOSE DASHBOARD");
        
        switchStep('step3-password', 'step4-success');
        currentStep = 4;
    }, 2000);
}

function switchStep(hideId, showId) {
    const hideEl = document.getElementById(hideId);
    const showEl = document.getElementById(showId);

    hideEl.style.opacity = '0';
    setTimeout(() => {
        hideEl.classList.add('hidden');
        showEl.classList.remove('hidden');
        void showEl.offsetWidth; 
        showEl.style.opacity = '1';
    }, 300);
}

function triggerError(message) {
    tg.HapticFeedback.notificationOccurred('error');
    tg.showAlert(message); 
}
