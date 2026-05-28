import os
import sys
import subprocess
import asyncio
import psutil
from flask import Flask, request, jsonify

# Setup Flask to serve the frontend from the 'webapp' folder
app = Flask(__name__, static_folder="webapp", static_url_path="")

# Core Storage Layout Config
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SESSION_DIR = os.path.join(BASE_DIR, "userbot_sessions")
SCRIPTS_DIR = os.path.join(BASE_DIR, "userbot_scripts")
os.makedirs(SESSION_DIR, exist_ok=True)
os.makedirs(SCRIPTS_DIR, exist_ok=True)

# Application state
ACTIVE_PROCESSES = {}
PENDING_HANDSHAKES = {}

# Telegram API Keys - REPLACE THESE WITH YOURS
API_ID = 1234567  
API_HASH = "your_api_hash_here"

# --- Process Management (Imported from sidhostingnew.py) ---
def kill_process_tree(process_info):
    """Safely terminate a process and its children using psutil."""
    try:
        if 'log_file' in process_info and not process_info['log_file'].closed:
            process_info['log_file'].close()

        process = process_info.get('process')
        if process and hasattr(process, 'pid'):
            parent = psutil.Process(process.pid)
            children = parent.children(recursive=True)
            for child in children:
                child.kill()
            parent.kill()
    except Exception as e:
        print(f"Error killing process: {e}")

# --- API Endpoints ---
@app.route('/')
def serve_homepage():
    return app.send_static_file('index.html')

@app.route('/api/deploy/initiate', methods=['POST'])
def initiate_handshake():
    data = request.json or {}
    phone = data.get("phone")
    script_code = data.get("script")

    if not phone or not script_code:
        return jsonify({"status": "error", "message": "Missing credentials."}), 400

    safe_phone = "".join(c for c in phone if c.isalnum() or c in "+")
    script_path = os.path.join(SCRIPTS_DIR, f"{safe_phone}_main.py")
    
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_code)

    try:
        from telethon import TelegramClient
        session_path = os.path.join(SESSION_DIR, f"sess_{safe_phone}")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        client = TelegramClient(session_path, API_ID, API_HASH, loop=loop)
        loop.run_until_complete(client.connect())
        code_hash_ref = loop.run_until_complete(client.send_code_request(phone))
        
        PENDING_HANDSHAKES[safe_phone] = {
            "client": client, "loop": loop, 
            "phone_code_hash": code_hash_ref.phone_code_hash,
            "script_path": script_path
        }
        return jsonify({"status": "awaiting_otp", "message": "OTP requested."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/deploy/verify-otp', methods=['POST'])
def verify_otp_challenge():
    data = request.json or {}
    phone = data.get("phone")
    otp_code = data.get("code")
    safe_phone = "".join(c for c in phone if c.isalnum() or c in "+")
    
    handshake = PENDING_HANDSHAKES.get(safe_phone)
    if not handshake: return jsonify({"status": "error", "message": "Session expired."}), 400

    try:
        asyncio.set_event_loop(handshake["loop"])
        from telethon.errors import SessionPasswordNeededError
        handshake["loop"].run_until_complete(handshake["client"].sign_in(
            phone=safe_phone, code=otp_code, phone_code_hash=handshake["phone_code_hash"]
        ))
        trigger_deployment(safe_phone, handshake["script_path"])
        del PENDING_HANDSHAKES[safe_phone]
        return jsonify({"status": "deployed"})
    except SessionPasswordNeededError:
        return jsonify({"status": "awaiting_2fa"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/deploy/finalize', methods=['POST'])
def finalize_cloud_password():
    data = request.json or {}
    phone = data.get("phone")
    password = data.get("password")
    safe_phone = "".join(c for c in phone if c.isalnum() or c in "+")
    
    handshake = PENDING_HANDSHAKES.get(safe_phone)
    if not handshake: return jsonify({"status": "error", "message": "Expired"}), 400

    try:
        asyncio.set_event_loop(handshake["loop"])
        handshake["loop"].run_until_complete(handshake["client"].sign_in(password=password))
        trigger_deployment(safe_phone, handshake["script_path"])
        del PENDING_HANDSHAKES[safe_phone]
        return jsonify({"status": "deployed"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 401

def trigger_deployment(phone_key, script_file_path):
    log_path = f"{script_file_path}.log"
    log_file_handle = open(log_path, "w", encoding="utf-8")
    proc = subprocess.Popen([sys.executable, script_file_path], stdout=log_file_handle, stderr=subprocess.STDOUT)
    ACTIVE_PROCESSES[phone_key] = {
        'process': proc,
        'log_file': log_file_handle,
        'log_path': log_path
    }

@app.route('/api/bot/control', methods=['POST'])
def control_threads():
    data = request.json or {}
    phone = data.get("phone")
    action = data.get("action")
    safe_phone = "".join(c for c in phone if c.isalnum() or c in "+")
    
    process_info = ACTIVE_PROCESSES.get(safe_phone)

    if action == "stop":
        if process_info:
            kill_process_tree(process_info)
            ACTIVE_PROCESSES.pop(safe_phone, None)
            return jsonify({"status": "stopped"})
        return jsonify({"status": "error", "message": "Not running."})
        
    elif action == "logs":
        log_path = os.path.join(SCRIPTS_DIR, f"{safe_phone}_main.py.log")
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                # Read last 100 lines for terminal
                lines = f.readlines()[-100:]
                return jsonify({"status": "success", "logs": "".join(lines)})
        return jsonify({"status": "success", "logs": "[System] No logs generated yet."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
