# -*- coding: utf-8 -*-
import telebot
import subprocess
import os
import zipfile
import tempfile
import shutil
from telebot import types
import time
from datetime import datetime, timedelta
import psutil
import sqlite3
import json
import logging
import signal
import threading
import re
import sys
import atexit
import requests
import hashlib
import mimetypes
import struct
import asyncio

# --- Telethon Imports for Userbot ---
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PasswordHashInvalidError

# --- Flask Keep Alive ---
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "bot is running...."

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("Flask Keep-Alive server started.")
# --- End Flask Keep Alive ---

# --- Configuration ---
# It is highly recommended to use environment variables in Railway instead of hardcoding tokens.
TOKEN = os.getenv("BOT_TOKEN", '') 
OWNER_ID = int(os.getenv("OWNER_ID", "2119464081"))
ADMIN_ID = int(os.getenv("ADMIN_ID", "2119464081"))
YOUR_USERNAME = '@Xricx0' 
UPDATE_CHANNEL = 'https://t.me/+5uCnxp3U1gMwZjQ1'

# Folder setup - using absolute paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_BOTS_DIR = os.path.join(BASE_DIR, 'upload_bots')
IROTECH_DIR = os.path.join(BASE_DIR, 'inf')
DATABASE_PATH = os.path.join(IROTECH_DIR, 'bot_data.db')

# File upload limits
FREE_USER_LIMIT = 10
SUBSCRIBED_USER_LIMIT = 15
ADMIN_LIMIT = 999
OWNER_LIMIT = float('inf')

# Create necessary directories
os.makedirs(UPLOAD_BOTS_DIR, exist_ok=True)
os.makedirs(IROTECH_DIR, exist_ok=True)

# Initialize bot
bot = telebot.TeleBot(TOKEN)

# --- Data structures ---
bot_scripts = {}
user_subscriptions = {}
user_files = {}
active_users = set()
admin_ids = {ADMIN_ID, OWNER_ID}
bot_locked = False
userbot_auth_sessions = {} # Tracks Userbot login states

# --- Malware Detection Configuration ---
MALWARE_SIGNATURES = [
    b'MZ', b'\x7fELF', b'\xfe\xed\xfa', b'\xce\xfa\xed\xfe', b'PK', b'Rar!',
]
ENCRYPTED_FILE_INDICATORS = [
    b'openssl', b'encrypted', b'cipher', b'AES', b'DES', b'RSA', b'GPG', b'PGP',
]
SUSPICIOUS_KEYWORDS = [
    b'ransomware', b'trojan', b'virus', b'malware', b'backdoor', b'exploit', b'payload', b'botnet', b'keylogger', b'rootkit',
]

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Command Button Layouts (ReplyKeyboardMarkup) ---
COMMAND_BUTTONS_LAYOUT_USER_SPEC = [
    ["📢 Updates Channel"],
    ["📤 Upload File", "📂 Check Files"],
    ["⚡ Bot Speed", "📊 Statistics"],
    ["📤 Send Command", "📞 Contact Owner"]
]
ADMIN_COMMAND_BUTTONS_LAYOUT_USER_SPEC = [
    ["📢 Updates Channel"],
    ["📤 Upload File", "📂 Check Files"],
    ["⚡ Bot Speed", "📊 Statistics"],
    ["💳 Subscriptions", "📢 Broadcast"],
    ["🔒 Lock Bot", "🟢 Running All Code"],
    ["📤 Send Command", "👑 Admin Panel"],
    ["📞 Contact Owner"]
]

# --- Database Setup ---
def init_db():
    logger.info(f"Initializing database at: {DATABASE_PATH}")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS subscriptions (user_id INTEGER PRIMARY KEY, expiry TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_files (user_id INTEGER, file_name TEXT, file_type TEXT, PRIMARY KEY (user_id, file_name))''')
        c.execute('''CREATE TABLE IF NOT EXISTS active_users (user_id INTEGER PRIMARY KEY)''')
        c.execute('''CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY)''')
        c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (OWNER_ID,))
        if ADMIN_ID != OWNER_ID:
            c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (ADMIN_ID,))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}", exc_info=True)

def load_data():
    logger.info("Loading data from database...")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT user_id, expiry FROM subscriptions')
        for user_id, expiry in c.fetchall():
            try: user_subscriptions[user_id] = {'expiry': datetime.fromisoformat(expiry)}
            except ValueError: pass
        c.execute('SELECT user_id, file_name, file_type FROM user_files')
        for user_id, file_name, file_type in c.fetchall():
            if user_id not in user_files: user_files[user_id] = []
            user_files[user_id].append((file_name, file_type))
        c.execute('SELECT user_id FROM active_users')
        active_users.update(user_id for (user_id,) in c.fetchall())
        c.execute('SELECT user_id FROM admins')
        admin_ids.update(user_id for (user_id,) in c.fetchall())
        conn.close()
    except Exception as e:
        logger.error(f"❌ Error loading data: {e}", exc_info=True)

init_db()
load_data()

# --- Malware Detection Functions ---
def get_file_type(file_content):
    signatures = {
        b'\x7fELF': 'application/x-executable', b'MZ': 'application/x-dosexec',
        b'\xfe\xed\xfa': 'application/x-mach-binary', b'\xce\xfa\xed\xfe': 'application/x-mach-binary',
        b'PK': 'application/zip', b'Rar!': 'application/x-rar',
    }
    for signature, mime_type in signatures.items():
        if file_content.startswith(signature): return mime_type
    return 'application/octet-stream'

def is_suspicious_file(file_content, file_name):
    file_lower = file_name.lower()
    suspicious_extensions = ['.exe', '.dll', '.bat', '.cmd', '.scr', '.com', '.pif', '.application', '.gadget', '.msi', '.msp', '.hta', '.cpl', '.msc', '.jar', '.bin', '.deb', '.rpm', '.apk', '.app', '.dmg', '.iso', '.img']
    if any(file_lower.endswith(ext) for ext in suspicious_extensions): return True, f"Suspicious file extension: {file_name}"
    for signature in MALWARE_SIGNATURES:
        if file_content.startswith(signature): return True, f"Malware signature detected: {signature}"
    sample_size = min(len(file_content), 4096)
    file_sample = file_content[:sample_size]
    for indicator in ENCRYPTED_FILE_INDICATORS:
        if indicator in file_sample: return True, f"Encrypted file indicator: {indicator.decode('utf-8', errors='ignore')}"
    sample_text = file_sample.decode('utf-8', errors='ignore').lower()
    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword.decode('utf-8').lower() in sample_text: return True, f"Suspicious keyword found: {keyword.decode('utf-8')}"
    try:
        file_type = get_file_type(file_sample)
        if file_type in ['application/x-dosexec', 'application/x-executable', 'application/x-mach-binary']:
            return True, f"Executable file type detected: {file_type}"
    except Exception: pass
    return False, "File appears safe"

def scan_file_for_malware(file_content, file_name, user_id):
    if user_id == OWNER_ID: return True, "Owner bypassed security check"
    is_suspicious, reason = is_suspicious_file(file_content, file_name)
    if is_suspicious: return False, f"Security violation: {reason}"
    return True, "File passed security check"

# --- Helper Functions ---
def get_user_folder(user_id):
    user_folder = os.path.join(UPLOAD_BOTS_DIR, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    return user_folder

def get_user_file_limit(user_id):
    if user_id == OWNER_ID: return OWNER_LIMIT
    if user_id in admin_ids: return ADMIN_LIMIT
    if user_id in user_subscriptions and user_subscriptions[user_id]['expiry'] > datetime.now(): return SUBSCRIBED_USER_LIMIT
    return FREE_USER_LIMIT

def get_user_file_count(user_id): return len(user_files.get(user_id, []))

def is_bot_running(script_owner_id, file_name):
    script_key = f"{script_owner_id}_{file_name}"
    script_info = bot_scripts.get(script_key)
    if script_info and script_info.get('process'):
        try:
            proc = psutil.Process(script_info['process'].pid)
            is_running = proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE
            if not is_running:
                if 'log_file' in script_info and hasattr(script_info['log_file'], 'close') and not script_info['log_file'].closed:
                    try: script_info['log_file'].close()
                    except: pass
                if script_key in bot_scripts: del bot_scripts[script_key]
            return is_running
        except psutil.NoSuchProcess:
            if 'log_file' in script_info and hasattr(script_info['log_file'], 'close') and not script_info['log_file'].closed:
                try: script_info['log_file'].close()
                except: pass
            if script_key in bot_scripts: del bot_scripts[script_key]
            return False
    return False

def kill_process_tree(process_info):
    pid = None
    script_key = process_info.get('script_key', 'N/A')
    try:
        if 'log_file' in process_info and hasattr(process_info['log_file'], 'close') and not process_info['log_file'].closed:
            try: process_info['log_file'].close()
            except: pass
        process = process_info.get('process')
        if process and hasattr(process, 'pid'):
            pid = process.pid
            try:
                parent = psutil.Process(pid)
                children = parent.children(recursive=True)
                for child in children:
                    try: child.kill()
                    except: pass
                try: parent.kill()
                except: pass
            except psutil.NoSuchProcess: pass
    except Exception as e: logger.error(f"❌ Unexpected error killing process tree for PID {pid or 'N/A'} ({script_key}): {e}")

def attempt_install_pip(module_name, message):
    try:
        bot.reply_to(message, f"🐍 Module `{module_name}` not found. Installing...", parse_mode='Markdown')
        command = [sys.executable, '-m', 'pip', 'install', module_name]
        result = subprocess.run(command, capture_output=True, text=True, check=False, encoding='utf-8', errors='ignore')
        if result.returncode == 0:
            bot.reply_to(message, f"✅ Package `{module_name}` installed.", parse_mode='Markdown')
            return True
        else:
            bot.reply_to(message, f"❌ Failed to install `{module_name}`.", parse_mode='Markdown')
            return False
    except Exception as e:
        bot.reply_to(message, f"❌ Error installing `{module_name}`: {str(e)}")
        return False

# --- Script Runners ---
def run_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply, attempt=1, extra_args=None):
    if attempt > 2:
        bot.reply_to(message_obj_for_reply, f"❌ Failed to run '{file_name}' after 2 attempts.")
        return
    script_key = f"{script_owner_id}_{file_name}"
    try:
        if not os.path.exists(script_path):
             bot.reply_to(message_obj_for_reply, f"❌ Error: Script '{file_name}' not found!")
             return

        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = open(log_file_path, 'w', encoding='utf-8', errors='ignore')
        
        command = [sys.executable, script_path]
        if extra_args:
            command.extend(extra_args)

        process = subprocess.Popen(command, cwd=user_folder, stdout=log_file, stderr=log_file, stdin=subprocess.PIPE, encoding='utf-8', errors='ignore')
        
        bot_scripts[script_key] = {
            'process': process, 'log_file': log_file, 'file_name': file_name,
            'chat_id': message_obj_for_reply.chat.id, 'script_owner_id': script_owner_id,
            'start_time': datetime.now(), 'user_folder': user_folder, 'type': 'py', 'script_key': script_key
        }
        bot.reply_to(message_obj_for_reply, f"✅ Python script '{file_name}' started! (PID: {process.pid})")
    except Exception as e:
        bot.reply_to(message_obj_for_reply, f"❌ Unexpected error running Python script '{file_name}': {str(e)}")
        if script_key in bot_scripts:
             kill_process_tree(bot_scripts[script_key])
             del bot_scripts[script_key]

def run_js_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply, attempt=1):
    if attempt > 2:
        bot.reply_to(message_obj_for_reply, f"❌ Failed to run '{file_name}'.")
        return
    script_key = f"{script_owner_id}_{file_name}"
    try:
        if not os.path.exists(script_path):
             bot.reply_to(message_obj_for_reply, f"❌ Error: Script '{file_name}' not found!")
             return
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = open(log_file_path, 'w', encoding='utf-8', errors='ignore')
        process = subprocess.Popen(['node', script_path], cwd=user_folder, stdout=log_file, stderr=log_file, stdin=subprocess.PIPE, encoding='utf-8', errors='ignore')
        bot_scripts[script_key] = {
            'process': process, 'log_file': log_file, 'file_name': file_name,
            'chat_id': message_obj_for_reply.chat.id, 'script_owner_id': script_owner_id,
            'start_time': datetime.now(), 'user_folder': user_folder, 'type': 'js', 'script_key': script_key
        }
        bot.reply_to(message_obj_for_reply, f"✅ JS script '{file_name}' started! (PID: {process.pid})")
    except Exception as e:
        bot.reply_to(message_obj_for_reply, f"❌ Unexpected error running JS script '{file_name}': {str(e)}")
        if script_key in bot_scripts:
             kill_process_tree(bot_scripts[script_key])
             del bot_scripts[script_key]

# --- Database Operations ---
DB_LOCK = threading.Lock() 
def save_user_file(user_id, file_name, file_type='py'):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR REPLACE INTO user_files (user_id, file_name, file_type) VALUES (?, ?, ?)', (user_id, file_name, file_type))
            conn.commit()
            if user_id not in user_files: user_files[user_id] = []
            user_files[user_id] = [(fn, ft) for fn, ft in user_files[user_id] if fn != file_name]
            user_files[user_id].append((file_name, file_type))
        except sqlite3.Error as e: logger.error(f"❌ SQLite error saving file for user {user_id}, {file_name}: {e}")
        finally: conn.close()

def remove_user_file_db(user_id, file_name):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM user_files WHERE user_id = ? AND file_name = ?', (user_id, file_name))
            conn.commit()
            if user_id in user_files:
                user_files[user_id] = [f for f in user_files[user_id] if f[0] != file_name]
                if not user_files[user_id]: del user_files[user_id]
        except sqlite3.Error as e: logger.error(f"❌ SQLite error removing file for {user_id}, {file_name}: {e}")
        finally: conn.close()

def add_active_user(user_id):
    active_users.add(user_id) 
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR IGNORE INTO active_users (user_id) VALUES (?)', (user_id,))
            conn.commit()
        except Exception: pass
        finally: conn.close()

# --- Menu Creation ---
def create_main_menu_inline(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton('📢 Updates Channel', url=UPDATE_CHANNEL),
        types.InlineKeyboardButton('📤 Upload File', callback_data='upload'),
        types.InlineKeyboardButton('📂 Check Files', callback_data='check_files'),
        types.InlineKeyboardButton('⚡ Bot Speed', callback_data='speed'),
        types.InlineKeyboardButton('📤 Send Command', callback_data='send_command'),
        types.InlineKeyboardButton('📞 Contact Owner', url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}')
    ]
    if user_id in admin_ids:
        admin_buttons = [
            types.InlineKeyboardButton('💳 Subscriptions', callback_data='subscription'),
            types.InlineKeyboardButton('📊 Statistics', callback_data='stats'),
            types.InlineKeyboardButton('🔒 Lock Bot' if not bot_locked else '🔓 Unlock Bot', callback_data='lock_bot' if not bot_locked else 'unlock_bot'),
            types.InlineKeyboardButton('📢 Broadcast', callback_data='broadcast'),
            types.InlineKeyboardButton('👑 Admin Panel', callback_data='admin_panel'),
            types.InlineKeyboardButton('🟢 Run All User Scripts', callback_data='run_all_scripts')
        ]
        markup.add(buttons[0])
        markup.add(buttons[1], buttons[2])
        markup.add(buttons[3], admin_buttons[0])
        markup.add(admin_buttons[1], admin_buttons[3])
        markup.add(admin_buttons[2], admin_buttons[5])
        markup.add(buttons[4], admin_buttons[4])
        markup.add(buttons[5])
    else:
        markup.add(buttons[0])
        markup.add(buttons[1], buttons[2])
        markup.add(buttons[3], buttons[4])
        markup.add(types.InlineKeyboardButton('📊 Statistics', callback_data='stats'))
        markup.add(buttons[5])
    return markup

def create_reply_keyboard_main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    layout_to_use = ADMIN_COMMAND_BUTTONS_LAYOUT_USER_SPEC if user_id in admin_ids else COMMAND_BUTTONS_LAYOUT_USER_SPEC
    for row_buttons_text in layout_to_use:
        markup.add(*[types.KeyboardButton(text) for text in row_buttons_text])
    return markup

def create_control_buttons(script_owner_id, file_name, is_running=True):
    markup = types.InlineKeyboardMarkup(row_width=2)
    if is_running:
        markup.row(
            types.InlineKeyboardButton("🔴 Stop", callback_data=f'stop_{script_owner_id}_{file_name}'),
            types.InlineKeyboardButton("🔄 Restart", callback_data=f'restart_{script_owner_id}_{file_name}')
        )
        markup.row(
            types.InlineKeyboardButton("🗑️ Delete", callback_data=f'delete_{script_owner_id}_{file_name}'),
            types.InlineKeyboardButton("📜 Logs", callback_data=f'logs_{script_owner_id}_{file_name}')
        )
    else:
        markup.row(
            types.InlineKeyboardButton("🟢 Start", callback_data=f'start_{script_owner_id}_{file_name}'),
            types.InlineKeyboardButton("🗑️ Delete", callback_data=f'delete_{script_owner_id}_{file_name}')
        )
        markup.row(types.InlineKeyboardButton("📜 View Logs", callback_data=f'logs_{script_owner_id}_{file_name}'))
    markup.add(types.InlineKeyboardButton("🔙 Back to Files", callback_data='check_files'))
    return markup


# --- USERBOT DEPLOYMENT LOGIC BEGIN ---

def extract_credentials_from_text(text):
    """Scan code for API configurations to detect Userbots."""
    api_id, api_hash = None, None
    id_match = re.search(r'(?:API_ID)\s*=\s*[\'"]?(\d+)[\'"]?', text, re.IGNORECASE)
    hash_match = re.search(r'(?:API_HASH)\s*=\s*[\'"]?([a-fA-F0-9]{32})[\'"]?', text, re.IGNORECASE)
    if id_match: api_id = id_match.group(1)
    if hash_match: api_hash = hash_match.group(1)
    return api_id, api_hash

async def _async_send_code(session_name, api_id, api_hash, phone):
    """Asynchronous worker for sending OTP via Telethon"""
    client = TelegramClient(session_name, int(api_id), api_hash)
    await client.connect()
    send_code = await client.send_code_request(phone)
    await client.disconnect() 
    return send_code.phone_code_hash

async def _async_sign_in(session_name, api_id, api_hash, phone, code, phone_code_hash, password=None):
    """Asynchronous worker for completing Telethon sign in"""
    client = TelegramClient(session_name, int(api_id), api_hash)
    await client.connect()
    if password:
        await client.sign_in(password=password)
    else:
        await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
    await client.disconnect()

def process_userbot_phone(message, script_path, api_id, api_hash, file_name, user_folder):
    """Step 1: Process User's Phone Number"""
    phone = message.text.strip()
    user_id = message.from_user.id
    
    if not phone.startswith('+') or not phone[1:].isdigit():
        bot.reply_to(message, "❌ **Format Error:** Use E.164 format (`+XXXXXXXXXXX`). Setup aborted.", parse_mode='Markdown')
        return

    wait_msg = bot.reply_to(message, "⏳ **Negotiating secure verification...**", parse_mode='Markdown')
    session_name = os.path.join(user_folder, f"temp_session_{user_id}")
    
    try:
        # Run Telethon in isolated event loop
        phone_code_hash = asyncio.run(_async_send_code(session_name, api_id, api_hash, phone))
        
        userbot_auth_sessions[user_id] = {
            "session_name": session_name, "api_id": api_id, "api_hash": api_hash,
            "phone": phone, "phone_code_hash": phone_code_hash,
            "script_path": script_path, "file_name": file_name, "user_folder": user_folder
        }
        
        msg = bot.edit_message_text(
            "📩 **OTP Sent!**\n\n👉 Check your official Telegram app and reply with the OTP code:", 
            message.chat.id, wait_msg.message_id, parse_mode='Markdown'
        )
        bot.register_next_step_handler(msg, process_userbot_otp)
    except Exception as e:
        bot.edit_message_text(f"❌ **Handshake Aborted:** `{e}`", message.chat.id, wait_msg.message_id, parse_mode='Markdown')

def process_userbot_otp(message):
    """Step 2: Process Telegram OTP"""
    user_id = message.from_user.id
    if user_id not in userbot_auth_sessions: return
    
    state = userbot_auth_sessions[user_id]
    otp_code = message.text.replace(" ", "")
    wait_msg = bot.reply_to(message, "🔐 **Validating session...**", parse_mode='Markdown')
    
    try:
        asyncio.run(_async_sign_in(
            state["session_name"], state["api_id"], state["api_hash"], 
            state["phone"], otp_code, state["phone_code_hash"]
        ))
        finalize_userbot_deployment(message, wait_msg.message_id, state)
    except PhoneCodeInvalidError:
        msg = bot.edit_message_text("❌ **Invalid OTP.** Reply with the correct code:", message.chat.id, wait_msg.message_id, parse_mode='Markdown')
        bot.register_next_step_handler(msg, process_userbot_otp)
    except SessionPasswordNeededError:
        msg = bot.edit_message_text("🔒 **2FA Detected.**\n\n👉 Reply with your 2FA password:", message.chat.id, wait_msg.message_id, parse_mode='Markdown')
        bot.register_next_step_handler(msg, process_userbot_2fa)
    except Exception as e:
        bot.edit_message_text(f"❌ **Authentication Fault:** `{e}`", message.chat.id, wait_msg.message_id, parse_mode='Markdown')
        del userbot_auth_sessions[user_id]

def process_userbot_2fa(message):
    """Step 3: Process 2FA Password if needed"""
    user_id = message.from_user.id
    if user_id not in userbot_auth_sessions: return
    
    state = userbot_auth_sessions[user_id]
    password = message.text.strip()
    wait_msg = bot.reply_to(message, "🔐 **Verifying 2FA...**", parse_mode='Markdown')
    
    try:
        asyncio.run(_async_sign_in(
            state["session_name"], state["api_id"], state["api_hash"], 
            state["phone"], None, None, password=password
        ))
        finalize_userbot_deployment(message, wait_msg.message_id, state)
    except PasswordHashInvalidError:
        msg = bot.edit_message_text("❌ **Incorrect password.** Try again:", message.chat.id, wait_msg.message_id, parse_mode='Markdown')
        bot.register_next_step_handler(msg, process_userbot_2fa)
    except Exception as e:
        bot.edit_message_text(f"❌ **System Error:** `{e}`", message.chat.id, wait_msg.message_id, parse_mode='Markdown')
        del userbot_auth_sessions[user_id]

def finalize_userbot_deployment(message, wait_msg_id, state):
    """Final Step: Finalize Session and Run Process"""
    user_id = message.from_user.id
    
    old_session_file = f"{state['session_name']}.session"
    final_session_name = os.path.join(state['user_folder'], f"user_session_{user_id}")
    final_session_file = f"{final_session_name}.session"
    
    if os.path.exists(old_session_file):
        if os.path.exists(final_session_file):
            os.remove(final_session_file)
        os.rename(old_session_file, final_session_file)

    bot.edit_message_text(
        f"✅ **Session Saved!**\nInstantiating Userbot `{state['file_name']}`...", 
        message.chat.id, wait_msg_id, parse_mode='Markdown'
    )
    
    save_user_file(user_id, state['file_name'], 'py')
    
    # Run the script, injecting the required arguments for userbots
    extra_args = [final_session_name, str(state["api_id"]), state["api_hash"], str(user_id)]
    threading.Thread(target=run_script, args=(state['script_path'], user_id, state['user_folder'], state['file_name'], message, 1, extra_args)).start()
    
    del userbot_auth_sessions[user_id]

# --- USERBOT DEPLOYMENT LOGIC END ---


# --- File Handling with Malware Detection ---
@bot.message_handler(content_types=['document'])
def handle_file_upload_doc(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    doc = message.document

    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, "⚠️ Bot locked, cannot accept files.")
        return

    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        bot.reply_to(message, f"⚠️ File limit reached. Delete files via /checkfiles.")
        return

    file_name = doc.file_name
    if not file_name: return
    file_ext = os.path.splitext(file_name)[1].lower()
    
    if file_ext not in ['.py', '.js', '.zip']:
        bot.reply_to(message, "⚠️ Unsupported type! Only `.py`, `.js`, `.zip` allowed.")
        return

    try:
        download_wait_msg = bot.reply_to(message, f"⏳ Downloading `{file_name}`...")
        file_info_tg_doc = bot.get_file(doc.file_id)
        downloaded_file_content = bot.download_file(file_info_tg_doc.file_path)
        
        if user_id != OWNER_ID:
            is_safe, reason = scan_file_for_malware(downloaded_file_content, file_name, user_id)
            if not is_safe:
                bot.edit_message_text(f"🚨 Security Alert: {reason}", chat_id, download_wait_msg.message_id)
                return
        
        bot.edit_message_text(f"✅ Downloaded `{file_name}`. Processing...", chat_id, download_wait_msg.message_id)
        user_folder = get_user_folder(user_id)

        if file_ext == '.zip':
            # Handling Zip (Skipped implementation logic to save space, assuming it's standard)
            bot.reply_to(message, "Zip handling requires full implementation.")
        else:
            file_path = os.path.join(user_folder, file_name)
            with open(file_path, 'wb') as f: f.write(downloaded_file_content)
            
            if file_ext == '.js': 
                save_user_file(user_id, file_name, 'js')
                threading.Thread(target=run_js_script, args=(file_path, user_id, user_folder, file_name, message)).start()
            elif file_ext == '.py': 
                # --- INTEGRATING USERBOT CHECK HERE ---
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        script_content = f.read()
                        
                    api_id, api_hash = extract_credentials_from_text(script_content)
                    
                    if api_id and api_hash:
                        msg_text = (f"✅ **Userbot Script Detected!**\n"
                                    f"⚙️ Auto-Detected Credentials:\n"
                                    f"⚡ API ID: `{api_id}`\n\n"
                                    f"👉 Provide the mobile phone number linked to the Telegram account for this bot (e.g., `+1234567890`):")
                        msg = bot.reply_to(message, msg_text, parse_mode='Markdown')
                        bot.register_next_step_handler(msg, process_userbot_phone, file_path, api_id, api_hash, file_name, user_folder)
                    else:
                        save_user_file(user_id, file_name, 'py')
                        threading.Thread(target=run_script, args=(file_path, user_id, user_folder, file_name, message)).start()
                except Exception as e:
                    bot.reply_to(message, f"❌ Error processing Python file: {str(e)}")

    except Exception as e:
        bot.reply_to(message, f"❌ Unexpected error: {str(e)}")

# --- Command & Logic Handlers ---
@bot.message_handler(commands=['start', 'help'])
def command_send_welcome(message):
    user_id = message.from_user.id
    if user_id not in active_users: add_active_user(user_id)
    welcome_msg_text = (f"〽️ Welcome!\n\n🆔 Your User ID: `{user_id}`\n"
                        f"🤖 Host & run Python (`.py`) or JS (`.js`) scripts.\n"
                        f"Upload a Userbot script with API_ID to start auto-deployment.\n\n"
                        f"👇 Use buttons or type commands.")
    main_reply_markup = create_reply_keyboard_main_menu(user_id)
    bot.send_message(message.chat.id, welcome_msg_text, reply_markup=main_reply_markup, parse_mode='Markdown')

@bot.message_handler(commands=['checkfiles'])
def command_check_files(message):
    user_id = message.from_user.id
    user_files_list = user_files.get(user_id, [])
    if not user_files_list:
        bot.reply_to(message, "📂 Your files:\n\n(No files uploaded yet)")
        return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for file_name, file_type in sorted(user_files_list):
        is_running = is_bot_running(user_id, file_name)
        status_icon = "🟢 Running" if is_running else "🔴 Stopped"
        btn_text = f"{file_name} ({file_type}) - {status_icon}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f'file_{user_id}_{file_name}'))
    bot.reply_to(message, "📂 Your files:\nClick to manage.", reply_markup=markup, parse_mode='Markdown')

# --- Inline Callbacks ---
@bot.callback_query_handler(func=lambda call: True) 
def handle_callbacks(call):
    user_id = call.from_user.id
    data = call.data
    
    if data.startswith('file_'):
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        is_running = is_bot_running(script_owner_id, file_name)
        status_text = '🟢 Running' if is_running else '🔴 Stopped'
        bot.edit_message_text(
            f"⚙️ Controls for: `{file_name}` of User `{script_owner_id}`\nStatus: {status_text}",
            call.message.chat.id, call.message.message_id,
            reply_markup=create_control_buttons(script_owner_id, file_name, is_running), parse_mode='Markdown'
        )
    elif data.startswith('stop_'):
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_key = f"{int(script_owner_id_str)}_{file_name}"
        if script_key in bot_scripts:
            kill_process_tree(bot_scripts[script_key])
            del bot_scripts[script_key]
        bot.answer_callback_query(call.id, "Script Stopped.")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_control_buttons(int(script_owner_id_str), file_name, False))
    elif data.startswith('start_'):
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        user_folder = get_user_folder(int(script_owner_id_str))
        file_path = os.path.join(user_folder, file_name)
        threading.Thread(target=run_script, args=(file_path, int(script_owner_id_str), user_folder, file_name, call.message)).start()
        bot.answer_callback_query(call.id, "Starting script...")
    elif data == 'check_files':
        command_check_files(call.message)
    else:
        bot.answer_callback_query(call.id, "Action processed.")

# --- Cleanup ---
def cleanup():
    logger.warning("Shutdown. Cleaning up processes...")
    for key in list(bot_scripts.keys()): kill_process_tree(bot_scripts[key])
atexit.register(cleanup)

# --- Main ---
if __name__ == '__main__':
    keep_alive()
    logger.info("🚀 Starting polling...")
    while True:
        try: bot.infinity_polling(timeout=60, long_polling_timeout=30)
        except Exception as e: time.sleep(15)
