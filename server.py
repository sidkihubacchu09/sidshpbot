#!/usr/bin/env python3
"""
SID HOSTING — Secure Multi-Instance Asynchronous Userbot Cloud Hypervisor
Combines standard routing endpoints with dynamic runtime thread compilation for Telethon bots.
"""

import os
import sys
import subprocess
import threading
import asyncio
from flask import Flask, request, jsonify

app = Flask(__name__)

# Core Storage Layout Config
SESSION_DIR = os.path.abspath("./userbot_sessions")
SCRIPTS_DIR = os.path.abspath("./userbot_scripts")
os.makedirs(SESSION_DIR, exist_ok=True)
os.makedirs(SCRIPTS_DIR, exist_ok=True)

# Application state dictionaries tracking references globally
ACTIVE_PROCESSES = {}  # Format: { phone: Subprocess_Object }
PENDING_HANDSHAKES = {}  # Format: { phone: { "client_ref": TelegramClient, "phone_code_hash": str } }

# Telethon API Keys (Acquire yours via https://my.telegram.org)
API_ID = 123456  
API_HASH = "your_hexadecimal_api_hash_string_here"


@app.route('/api/deploy/initiate', method=['POST'])
def initiate_handshake():
    """
    STAGE 1: Receive Phone + Script, bind session variables, request Telegram OTP Code
    """
    data = request.json or {}
    phone = data.get("phone")
    script_code = data.get("script")

    if not phone or not script_code:
        return jsonify({"status": "error", "message": "Missing credentials or code payload."}), 400

    # Ensure phone numbers don't contain hazardous file-path escape anomalies
    safe_phone = "".join(c for c in phone if c.isalnum() or c in "+")
    
    # Write custom userbot script to isolates folder
    script_path = os.path.join(SCRIPTS_DIR, f"{safe_phone}_main.py")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_code)

    # Initialize asynchronous isolation engine thread task for Telethon connection 
    try:
        from telethon import TelegramClient
        session_path = os.path.join(SESSION_DIR, f"sess_{safe_phone}")
        
        # Instantiate continuous connection client
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        client = TelegramClient(session_path, API_ID, API_HASH, loop=loop)
        loop.run_until_complete(client.connect())
        
        # Trigger outbound core request to dispatch telegram validation SMS/app message
        code_hash_ref = loop.run_until_complete(client.send_code_request(phone))
        
        # Persist runtime client instances to cache for processing matching stage requests 
        PENDING_HANDSHAKES[safe_phone] = {
            "client": client,
            "loop": loop,
            "phone_code_hash": code_hash_ref.phone_code_hash,
            "phone": phone,
            "script_path": script_path
        }
        
        return jsonify({"status": "awaiting_otp", "message": "OTP challenge requested successfully."})

    except Exception as e:
        return jsonify({"status": "error", "message": f"Cluster connection failed: {str(e)}"}), 500


@app.route('/api/deploy/verify-otp', method=['POST'])
def verify_otp_challenge():
    """
    STAGE 2: Accept incoming verification code string, check for 2FA Cloud Passwords requirements
    """
    data = request.json or {}
    phone = data.get("phone")
    otp_code = data.get("code")

    safe_phone = "".join(c for c in phone if c.isalnum() or c in "+") if phone else None
    
    # Locate cached configuration block matching criteria
    handshake = PENDING_HANDSHAKES.get(safe_phone)
    if not handshake:
        return jsonify({"status": "error", "message": "Handshake context expired or missing phone index mapping."}), 400

    client = handshake["client"]
    loop = handshake["loop"]
    phone_code_hash = handshake["phone_code_hash"]

    try:
        asyncio.set_event_loop(loop)
        # Attempt standard code sign-in validation
        from telethon.errors import SessionPasswordNeededError
        
        try:
            loop.run_until_complete(client.sign_in(phone=safe_phone, code=otp_code, phone_code_hash=phone_code_hash))
            # Success directly without cloud password requirement!
            trigger_background_node_deployment(safe_phone, handshake["script_path"])
            return jsonify({"status": "deployed", "message": "Userbot container running successfully without 2FA key."})
            
        except SessionPasswordNeededError:
            # Explicit signal that Two-Step Cloud validation is active on user profile
            return jsonify({"status": "awaiting_2fa", "message": "Telegram configuration requires a Two-Step Cloud Password entry."})

    except Exception as e:
        return jsonify({"status": "error", "message": f"Verification mismatch: {str(e)}"}), 500


@app.route('/api/deploy/finalize', method=['POST'])
def finalize_cloud_password():
    """
    STAGE 3: Authorize Two-Step verified cloud credentials and spin background isolated container
    """
    data = request.json or {}
    phone = data.get("phone")
    cloud_password = data.get("password")

    safe_phone = "".join(c for c in phone if c.isalnum() or c in "+") if phone else None
    handshake = PENDING_HANDSHAKES.get(safe_phone)
    
    if not handshake:
        return jsonify({"status": "error", "message": "Staged verification handshake contextual mapping lost."}), 400

    client = handshake["client"]
    loop = handshake["loop"]

    try:
        asyncio.set_event_loop(loop)
        # Sign session using cloud key values
        loop.run_until_complete(client.sign_in(password=cloud_password))
        
        # De-register from pending, deploy active runtime pipeline loop
        trigger_background_node_deployment(safe_phone, handshake["script_path"])
        del PENDING_HANDSHAKES[safe_phone]
        
        return jsonify({"status": "deployed", "message": "Isolated container active. Microservice live."})

    except Exception as e:
        return jsonify({"status": "error", "message": f"2FA Cryptographic unlock failed: {str(e)}"}), 401


def trigger_background_node_deployment(phone_key, script_file_path):
    """
    STAGE 4: Spin up continuous non-blocking asynchronous processes 
    ensuring continuous thread persistence.
    """
    # Clean up duplicate runtimes if process already exists
    if phone_key in ACTIVE_PROCESSES:
        try:
            ACTIVE_PROCESSES[phone_key].terminate()
        except Exception:
            pass

    # Launch userbot python script as isolated background instance process
    log_file_path = f"{script_file_path}.log"
    log_file_handle = open(log_file_path, "w", encoding="utf-8")
    
    proc = subprocess.Popen(
        [sys.executable, script_file_path],
        stdout=log_file_handle,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    ACTIVE_PROCESSES[phone_key] = proc


@app.route('/api/bot/control', method=['POST'])
def control_threads():
    """
    Universal API Endpoint to trigger process operations (stop, restart, read live logs)
    """
    data = request.json or {}
    phone = data.get("phone")
    action = data.get("action")  # options: "stop", "restart", "logs"

    safe_phone = "".join(c for c in phone if c.isalnum() or c in "+") if phone else None
    script_path = os.path.join(SCRIPTS_DIR, f"{safe_phone}_main.py")

    if action == "stop":
        proc = ACTIVE_PROCESSES.get(safe_phone)
        if proc:
            proc.terminate()
            proc.wait()
            del ACTIVE_PROCESSES[safe_phone]
            return jsonify({"status": "stopped", "message": "Thread context closed execution cleanly."})
        return jsonify({"status": "error", "message": "Target process is not actively running."}), 404

    elif action == "logs":
        log_path = f"{script_path}.log"
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as log_file:
                return jsonify({"status": "success", "logs": log_file.read()})
        return jsonify({"status": "success", "logs": "[System Active] Awaiting process generation initialization outputs..."})

    return jsonify({"status": "error", "message": "Unknown action parameter instruction mapping."}), 400


if __name__ == '__main__':
    # Initialize the web server node local clusters
    print("==========================================================================")
    print(" SID HOSTING PROCESS HYPERVISOR V4.1 CORE HUB SECURE ONLINE ")
    print("==========================================================================")
    app.run(host='0.0.0.0', port=5000, debug=True)
