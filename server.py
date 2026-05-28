#!/usr/bin/env python3
import os
import sys
import subprocess
import asyncio
from flask import Flask, request, jsonify

# --- ADJUSTMENT: Configure Flask to serve static files from the 'webapp' folder ---
# This allows your index.html to access /css/style.css and /js/script.js automatically.
app = Flask(__name__, static_folder="webapp", static_url_path="https://worker-production-69b2.up.railway.app/")

# Core Storage Layout Config
SESSION_DIR = os.path.abspath("./userbot_sessions")
SCRIPTS_DIR = os.path.abspath("./userbot_scripts")
os.makedirs(SESSION_DIR, exist_ok=True)
os.makedirs(SCRIPTS_DIR, exist_ok=True)

# Application state dictionaries
ACTIVE_PROCESSES = {}
PENDING_HANDSHAKES = {}

# Telegram API Keys
API_ID = 123456  
API_HASH = "your_hexadecimal_api_hash_string_here"

# --- Serve the Frontend ---
@app.route('/')
def serve_homepage():
    return app.send_static_file('index.html')

# --- API Endpoints ---
@app.route('/api/deploy/initiate', methods=['POST'])
def initiate_handshake():
    data = request.json or {}
    phone = data.get("phone")
    script_code = data.get("script")

    if not phone or not script_code:
        return jsonify({"status": "error", "message": "Missing credentials or code payload."}), 400

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
    safe_phone = "".join(c for c in phone if c.isalnum() or c in "+") if phone else None
    
    handshake = PENDING_HANDSHAKES.get(safe_phone)
    if not handshake: return jsonify({"status": "error", "message": "Expired"}), 400

    try:
        asyncio.set_event_loop(handshake["loop"])
        from telethon.errors import SessionPasswordNeededError
        handshake["loop"].run_until_complete(handshake["client"].sign_in(
            phone=safe_phone, code=otp_code, phone_code_hash=handshake["phone_code_hash"]
        ))
        trigger_background_node_deployment(safe_phone, handshake["script_path"])
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
    safe_phone = "".join(c for c in phone if c.isalnum() or c in "+") if phone else None
    handshake = PENDING_HANDSHAKES.get(safe_phone)
    
    if not handshake: return jsonify({"status": "error", "message": "Expired"}), 400

    try:
        asyncio.set_event_loop(handshake["loop"])
        handshake["loop"].run_until_complete(handshake["client"].sign_in(password=password))
        trigger_background_node_deployment(safe_phone, handshake["script_path"])
        del PENDING_HANDSHAKES[safe_phone]
        return jsonify({"status": "deployed"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 401

def trigger_background_node_deployment(phone_key, script_file_path):
    log_file_handle = open(f"{script_file_path}.log", "w", encoding="utf-8")
    proc = subprocess.Popen([sys.executable, script_file_path], stdout=log_file_handle, stderr=subprocess.STDOUT)
    ACTIVE_PROCESSES[phone_key] = proc

@app.route('/api/bot/control', methods=['POST'])
def control_threads():
    data = request.json or {}
    phone = data.get("phone")
    action = data.get("action")
    safe_phone = "".join(c for c in phone if c.isalnum() or c in "+") if phone else None
    
    if action == "stop":
        proc = ACTIVE_PROCESSES.pop(safe_phone, None)
        if proc: proc.terminate()
        return jsonify({"status": "stopped"})
    elif action == "logs":
        log_path = os.path.join(SCRIPTS_DIR, f"{safe_phone}_main.py.log")
        logs = open(log_path, "r").read() if os.path.exists(log_path) else "No logs yet."
        return jsonify({"status": "success", "logs": logs})
    return jsonify({"status": "error"}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
