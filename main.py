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
TOKEN = os.getenv("BOT_TOKEN", '') 
OWNER_ID = int(os.getenv("OWNER_ID", "2119464081"))
ADMIN_ID = int(os.getenv("ADMIN_ID", "2119464081"))
YOUR_USERNAME = '@Xricx0' 
UPDATE_CHANNEL = 'https://t.me/+5uCnxp3U1gMwZjQ1'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_BOTS_DIR = os.path.join(BASE_DIR, 'upload_bots')
IROTECH_DIR = os.path.join(BASE_DIR, 'inf')
DATABASE_PATH = os.path.join(IROTECH_DIR, 'bot_data.db')

FREE_USER_LIMIT = 10
SUBSCRIBED_USER_LIMIT = 15
ADMIN_LIMIT = 999
OWNER_LIMIT = float('inf')

os.makedirs(UPLOAD_BOTS_DIR, exist_ok=True)
os.makedirs(IROTECH_DIR, exist_ok=True)

bot = telebot.TeleBot(TOKEN)

bot_scripts = {}
user_subscriptions = {}
user_files = {}
active_users = set()
admin_ids = {ADMIN_ID, OWNER_ID}
bot_locked = False
userbot_auth_sessions = {}

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Command Button Layouts ---
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
        logger.error(f"❌ Database error: {e}")

def load_data():
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
        logger.error(f"❌ Error loading data: {e}")

init_db()
load_data()

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
                if script_key in bot_scripts: del bot_scripts[script_key]
            return is_running
        except psutil.NoSuchProcess:
            if script_key in bot_scripts: del bot_scripts[script_key]
            return False
    return False

def kill_process_tree(process_info):
    pid = None
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
    except Exception as e: logger.error(f"❌ Error killing PID {pid}: {e}")

# --- Script Runners ---
def run_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply, attempt=1, extra_args=None):
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
        
        command = [sys.executable, script_path]
        if extra_args: command.extend(extra_args)

        process = subprocess.Popen(command, cwd=user_folder, stdout=log_file, stderr=log_file, stdin=subprocess.PIPE, encoding='utf-8', errors='ignore')
        
        bot_scripts[script_key] = {
            'process': process, 'log_file': log_file, 'file_name': file_name,
            'chat_id': message_obj_for_reply.chat.id, 'script_owner_id': script_owner_id,
            'start_time': datetime.now(), 'user_folder': user_folder, 'type': 'py', 'script_key': script_key
        }
        bot.reply_to(message_obj_for_reply, f"✅ Python script '{file_name}' started! (PID: {process.pid})")
    except Exception as e:
        bot.reply_to(message_obj_for_reply, f"❌ Unexpected error running script: {str(e)}")
        if script_key in bot_scripts:
             kill_process_tree(bot_scripts[script_key])
             del bot_scripts[script_key]

def run_js_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply, attempt=1):
    script_key = f"{script_owner_id}_{file_name}"
    try:
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
        bot.reply_to(message_obj_for_reply, f"❌ Error running JS script: {str(e)}")

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
        except sqlite3.Error as e: logger.error(f"❌ DB error: {e}")
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
        except sqlite3.Error as e: logger.error(f"❌ DB error: {e}")
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
def create_reply_keyboard_main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    layout_to_use = ADMIN_COMMAND_BUTTONS_LAYOUT_USER_SPEC if user_id in admin_ids else COMMAND_BUTTONS_LAYOUT_USER_SPEC
    for row_buttons_text in layout_to_use:
        markup.add(*[types.KeyboardButton(text) for text in row_buttons_text])
    return markup

def create_control_buttons(script_owner_id, file_name, is_running=True):
    markup = types.InlineKeyboardMarkup(row_width=2)
    if is_running:
        markup.row(types.InlineKeyboardButton("🔴 Stop", callback_data=f'stop_{script_owner_id}_{file_name}'),
                   types.InlineKeyboardButton("🔄 Restart", callback_data=f'restart_{script_owner_id}_{file_name}'))
        markup.row(types.InlineKeyboardButton("🗑️ Delete", callback_data=f'delete_{script_owner_id}_{file_name}'),
                   types.InlineKeyboardButton("📜 Logs", callback_data=f'logs_{script_owner_id}_{file_name}'))
    else:
        markup.row(types.InlineKeyboardButton("🟢 Start", callback_data=f'start_{script_owner_id}_{file_name}'),
                   types.InlineKeyboardButton("🗑️ Delete", callback_data=f'delete_{script_owner_id}_{file_name}'))
        markup.row(types.InlineKeyboardButton("📜 View Logs", callback_data=f'logs_{script_owner_id}_{file_name}'))
    return markup

# --- USERBOT DEPLOYMENT LOGIC BEGIN ---
def extract_credentials_from_text(text):
    api_id, api_hash = None, None
    id_match = re.search(r'(?:API_ID)\s*=\s*[\'"]?(\d+)[\'"]?', text, re.IGNORECASE)
    hash_match = re.search(r'(?:API_HASH)\s*=\s*[\'"]?([a-fA-F0-9]{32})[\'"]?', text, re.IGNORECASE)
    if id_match: api_id = id_match.group(1)
    if hash_match: api_hash = hash_match.group(1)
    return api_id, api_hash

async def _async_send_code(session_name, api_id, api_hash, phone):
    client = TelegramClient(session_name, int(api_id), api_hash)
    await client.connect()
    send_code = await client.send_code_request(phone)
    await client.disconnect() 
    return send_code.phone_code_hash

async def _async_sign_in(session_name, api_id, api_hash, phone, code, phone_code_hash, password=None):
    client = TelegramClient(session_name, int(api_id), api_hash)
    await client.connect()
    if password: await client.sign_in(password=password)
    else: await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
    await client.disconnect()

def process_userbot_phone(message, script_path, api_id, api_hash, file_name, user_folder):
    phone = message.text.strip()
    user_id = message.from_user.id
    if not phone.startswith('+') or not phone[1:].isdigit():
        bot.reply_to(message, "❌ **Format Error:** Use E.164 format (`+XXXXXXXXXXX`). Setup aborted.", parse_mode='Markdown')
        return
    wait_msg = bot.reply_to(message, "⏳ **Negotiating secure verification...**", parse_mode='Markdown')
    session_name = os.path.join(user_folder, f"temp_session_{user_id}")
    try:
        phone_code_hash = asyncio.run(_async_send_code(session_name, api_id, api_hash, phone))
        userbot_auth_sessions[user_id] = {
            "session_name": session_name, "api_id": api_id, "api_hash": api_hash,
            "phone": phone, "phone_code_hash": phone_code_hash,
            "script_path": script_path, "file_name": file_name, "user_folder": user_folder
        }
        msg = bot.edit_message_text("📩 **OTP Sent!**\n\n👉 Reply with the OTP code:", message.chat.id, wait_msg.message_id, parse_mode='Markdown')
        bot.register_next_step_handler(msg, process_userbot_otp)
    except Exception as e:
        bot.edit_message_text(f"❌ **Handshake Aborted:** `{e}`", message.chat.id, wait_msg.message_id, parse_mode='Markdown')

def process_userbot_otp(message):
    user_id = message.from_user.id
    if user_id not in userbot_auth_sessions: return
    state = userbot_auth_sessions[user_id]
    otp_code = message.text.replace(" ", "")
    wait_msg = bot.reply_to(message, "🔐 **Validating session...**", parse_mode='Markdown')
    try:
        asyncio.run(_async_sign_in(state["session_name"], state["api_id"], state["api_hash"], state["phone"], otp_code, state["phone_code_hash"]))
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
    user_id = message.from_user.id
    if user_id not in userbot_auth_sessions: return
    state = userbot_auth_sessions[user_id]
    password = message.text.strip()
    wait_msg = bot.reply_to(message, "🔐 **Verifying 2FA...**", parse_mode='Markdown')
    try:
        asyncio.run(_async_sign_in(state["session_name"], state["api_id"], state["api_hash"], state["phone"], None, None, password=password))
        finalize_userbot_deployment(message, wait_msg.message_id, state)
    except PasswordHashInvalidError:
        msg = bot.edit_message_text("❌ **Incorrect password.** Try again:", message.chat.id, wait_msg.message_id, parse_mode='Markdown')
        bot.register_next_step_handler(msg, process_userbot_2fa)
    except Exception as e:
        bot.edit_message_text(f"❌ **System Error:** `{e}`", message.chat.id, wait_msg.message_id, parse_mode='Markdown')
        del userbot_auth_sessions[user_id]

def finalize_userbot_deployment(message, wait_msg_id, state):
    user_id = message.from_user.id
    old_session_file = f"{state['session_name']}.session"
    final_session_name = os.path.join(state['user_folder'], f"user_session_{user_id}")
    final_session_file = f"{final_session_name}.session"
    
    if os.path.exists(old_session_file):
        if os.path.exists(final_session_file): os.remove(final_session_file)
        os.rename(old_session_file, final_session_file)

    bot.edit_message_text(f"✅ **Session Saved!**\nInstantiating Userbot `{state['file_name']}`...", message.chat.id, wait_msg_id, parse_mode='Markdown')
    save_user_file(user_id, state['file_name'], 'py')
    
    extra_args = [final_session_name, str(state["api_id"]), state["api_hash"], str(user_id)]
    threading.Thread(target=run_script, args=(state['script_path'], user_id, state['user_folder'], state['file_name'], message, 1, extra_args)).start()
    del userbot_auth_sessions[user_id]

# --- ZIP Handling ---
def handle_zip_file(downloaded_file_content, file_name_zip, message):
    user_id = message.from_user.id
    user_folder = get_user_folder(user_id)
    temp_dir = tempfile.mkdtemp(prefix=f"user_{user_id}_zip_")
    
    try:
        zip_path = os.path.join(temp_dir, file_name_zip)
        with open(zip_path, 'wb') as new_file:
            new_file.write(downloaded_file_content)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        target_dir = temp_dir
        for root, dirs, files in os.walk(temp_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('__')]
            if any(f.endswith(('.py', '.js')) for f in files):
                target_dir = root
                break
        
        if target_dir != temp_dir:
            for item in os.listdir(target_dir):
                s = os.path.join(target_dir, item)
                d = os.path.join(temp_dir, item)
                if os.path.exists(d):
                    if os.path.isdir(d): shutil.rmtree(d)
                    else: os.remove(d)
                shutil.move(s, d)
        
        extracted_items = os.listdir(temp_dir)
        py_files = [f for f in extracted_items if f.endswith('.py')]
        js_files = [f for f in extracted_items if f.endswith('.js')]
        req_file = 'requirements.txt' if 'requirements.txt' in extracted_items else None

        if req_file:
            req_path = os.path.join(temp_dir, req_file)
            bot.reply_to(message, f"🔄 Installing Python deps from `{req_file}`...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', req_path], capture_output=True, check=False)

        main_script_name = None; file_type = None
        preferred_py = ['main.py', 'bot.py', 'app.py']
        for p in preferred_py:
            if p in py_files: main_script_name = p; file_type = 'py'; break
        if not main_script_name and py_files: main_script_name = py_files[0]; file_type = 'py'
        if not main_script_name and js_files: main_script_name = js_files[0]; file_type = 'js'

        if not main_script_name:
            bot.reply_to(message, "❌ No `.py` or `.js` script found in archive!"); return

        for item_name in os.listdir(temp_dir):
            if item_name == file_name_zip: continue 
            src_path = os.path.join(temp_dir, item_name)
            dest_path = os.path.join(user_folder, item_name)
            if os.path.isdir(dest_path): shutil.rmtree(dest_path)
            elif os.path.exists(dest_path): os.remove(dest_path)
            shutil.move(src_path, dest_path)

        save_user_file(user_id, main_script_name, file_type)
        main_script_path = os.path.join(user_folder, main_script_name)
        bot.reply_to(message, f"✅ Files extracted. Starting main script: `{main_script_name}`...", parse_mode='Markdown')

        if file_type == 'py':
             threading.Thread(target=run_script, args=(main_script_path, user_id, user_folder, main_script_name, message)).start()
        elif file_type == 'js':
             threading.Thread(target=run_js_script, args=(main_script_path, user_id, user_folder, main_script_name, message)).start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error processing zip: {str(e)}")
    finally:
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)

# --- File Handling ---
@bot.message_handler(content_types=['document'])
def handle_file_upload_doc(message):
    user_id = message.from_user.id
    doc = message.document

    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, "⚠️ Bot locked, cannot accept files.")
        return

    if get_user_file_count(user_id) >= get_user_file_limit(user_id):
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
        
        bot.edit_message_text(f"✅ Downloaded `{file_name}`. Processing...", message.chat.id, download_wait_msg.message_id)
        user_folder = get_user_folder(user_id)

        if file_ext == '.zip':
            handle_zip_file(downloaded_file_content, file_name, message)
        else:
            file_path = os.path.join(user_folder, file_name)
            with open(file_path, 'wb') as f: f.write(downloaded_file_content)
            
            if file_ext == '.js': 
                save_user_file(user_id, file_name, 'js')
                threading.Thread(target=run_js_script, args=(file_path, user_id, user_folder, file_name, message)).start()
            elif file_ext == '.py': 
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


# --- Button Logic Handlers ---
def _logic_send_welcome(message):
    user_id = message.from_user.id
    if user_id not in active_users: add_active_user(user_id)
    welcome_msg_text = (f"〽️ Welcome!\n\n🆔 Your User ID: `{user_id}`\n"
                        f"🤖 Host & run Python (`.py`) or JS (`.js`) scripts.\n"
                        f"Upload a Userbot script with API_ID to start auto-deployment.\n\n"
                        f"👇 Use buttons or type commands.")
    main_reply_markup = create_reply_keyboard_main_menu(user_id)
    bot.send_message(message.chat.id, welcome_msg_text, reply_markup=main_reply_markup, parse_mode='Markdown')

def _logic_check_files(message):
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

def _logic_upload_file(message):
    bot.reply_to(message, "📤 Send your Python (`.py`), JS (`.js`), or ZIP (`.zip`) file.")

def _logic_bot_speed(message):
    start_time = time.time()
    msg = bot.reply_to(message, "🏃 Testing speed...")
    latency = round((time.time() - start_time) * 1000, 2)
    bot.edit_message_text(f"⚡ Bot Speed:\n\n⏱️ Response Time: {latency} ms", message.chat.id, msg.message_id)

def _logic_statistics(message):
    total_users = len(active_users)
    bot.reply_to(message, f"📊 Bot Statistics:\n\n👥 Total Users: {total_users}")

# --- Command Routing ---
BUTTON_TEXT_TO_LOGIC = {
    "📢 Updates Channel": lambda m: bot.reply_to(m, f"Visit our Updates Channel: {UPDATE_CHANNEL}"),
    "📤 Upload File": _logic_upload_file,
    "📂 Check Files": _logic_check_files,
    "⚡ Bot Speed": _logic_bot_speed,
    "📊 Statistics": _logic_statistics,
    "📞 Contact Owner": lambda m: bot.reply_to(m, f"Contact: {YOUR_USERNAME}")
}

@bot.message_handler(commands=['start', 'help'])
def command_start(message): _logic_send_welcome(message)

@bot.message_handler(commands=['checkfiles'])
def command_files(message): _logic_check_files(message)

@bot.message_handler(func=lambda message: message.text in BUTTON_TEXT_TO_LOGIC)
def handle_button_text(message):
    logic_func = BUTTON_TEXT_TO_LOGIC.get(message.text)
    if logic_func: logic_func(message)

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
    elif data.startswith('delete_'):
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        script_key = f"{script_owner_id}_{file_name}"
        if script_key in bot_scripts:
            kill_process_tree(bot_scripts[script_key])
            del bot_scripts[script_key]
        remove_user_file_db(script_owner_id, file_name)
        bot.answer_callback_query(call.id, "File deleted.")
        bot.edit_message_text("File deleted successfully.", call.message.chat.id, call.message.message_id)
    elif data == 'check_files':
        _logic_check_files(call.message)
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
