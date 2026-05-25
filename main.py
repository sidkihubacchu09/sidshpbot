# -*- coding: utf-8 -*-
import telebot
import subprocess
import os
import sqlite3
import logging
import threading
import sys
import atexit
import time
from datetime import datetime
import psutil
from telebot import types
from flask import Flask
from threading import Thread

# --- Configuration ---
TOKEN = '8032494974:AAE3s6Uh0c-KdWsXDd5ZP_R6h6KixSUt-dw' 
OWNER_ID = 2119464081
ADMIN_ID = 2119464081
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

# --- Flask Keep Alive ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running securely...."

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("Flask Keep-Alive started.")
# --- End Flask Keep Alive ---

# --- Data structures ---
bot_scripts = {}
user_subscriptions = {}
user_files = {}
active_users = set()
admin_ids = {ADMIN_ID, OWNER_ID}
bot_locked = False

# --- Malware Detection Configuration ---
MALWARE_SIGNATURES = [
    b'MZ', b'\x7fELF', b'\xfe\xed\xfa', b'\xce\xfa\xed\xfe', b'PK', b'Rar!',
]
ENCRYPTED_FILE_INDICATORS = [
    b'openssl', b'encrypted', b'cipher', b'AES', b'DES', b'RSA', b'GPG', b'PGP',
]
SUSPICIOUS_KEYWORDS = [
    b'ransomware', b'trojan', b'virus', b'malware', b'backdoor', 
    b'exploit', b'payload', b'botnet', b'keylogger', b'rootkit',
]

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
        c.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
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

DB_LOCK = threading.Lock() 

def save_user_file(user_id, file_name, file_type='py'):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR REPLACE INTO user_files (user_id, file_name, file_type) VALUES (?, ?, ?)',
                      (user_id, file_name, file_type))
            conn.commit()
            if user_id not in user_files: user_files[user_id] = []
            user_files[user_id] = [(fn, ft) for fn, ft in user_files[user_id] if fn != file_name]
            user_files[user_id].append((file_name, file_type))
        except Exception as e: logger.error(f"Error saving file: {e}")
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
        except Exception as e: logger.error(f"Error removing file: {e}")
        finally: conn.close()

def save_menu_video_id(file_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', ('menu_video_id', file_id))
        conn.commit()
        conn.close()

def get_menu_video_id():
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT value FROM settings WHERE key = ?', ('menu_video_id',))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None

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
    suspicious_extensions = ['.exe', '.dll', '.bat', '.cmd', '.scr', '.com', '.pif', '.application', '.gadget',
                            '.msi', '.msp', '.com', '.scr', '.hta', '.cpl', '.msc', '.jar', '.bin', '.deb', '.rpm',
                            '.apk', '.app', '.dmg', '.iso', '.img']
    if any(file_lower.endswith(ext) for ext in suspicious_extensions):
        return True, f"Suspicious file extension: {file_name}"
    for signature in MALWARE_SIGNATURES:
        if file_content.startswith(signature): return True, f"Malware signature detected"
    
    sample_size = min(len(file_content), 4096)
    file_sample = file_content[:sample_size]
    for indicator in ENCRYPTED_FILE_INDICATORS:
        if indicator in file_sample: return True, f"Encrypted file indicator"
    sample_text = file_sample.decode('utf-8', errors='ignore').lower()
    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword.decode('utf-8').lower() in sample_text: return True, f"Suspicious keyword found"
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
    if user_id in user_subscriptions and user_subscriptions[user_id]['expiry'] > datetime.now():
        return SUBSCRIBED_USER_LIMIT
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
                if 'log_file' in script_info and not script_info['log_file'].closed: script_info['log_file'].close()
                if script_key in bot_scripts: del bot_scripts[script_key]
            return is_running
        except psutil.NoSuchProcess:
            if 'log_file' in script_info and not script_info['log_file'].closed: script_info['log_file'].close()
            if script_key in bot_scripts: del bot_scripts[script_key]
            return False
    return False

def kill_process_tree(process_info):
    try:
        if 'log_file' in process_info and not process_info['log_file'].closed: process_info['log_file'].close()
        process = process_info.get('process')
        if process and hasattr(process, 'pid'):
            pid = process.pid
            try:
                parent = psutil.Process(pid)
                children = parent.children(recursive=True)
                for child in children:
                    try: child.kill()
                    except psutil.NoSuchProcess: pass
                psutil.wait_procs(children, timeout=1)
                try: parent.kill()
                except psutil.NoSuchProcess: pass
            except psutil.NoSuchProcess: pass
    except Exception as e: logger.error(f"Error killing process: {e}")

# --- Menu creation ---
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
            types.InlineKeyboardButton('🔒 Lock Bot' if not bot_locked else '🔓 Unlock Bot',
                                     callback_data='lock_bot' if not bot_locked else 'unlock_bot'),
            types.InlineKeyboardButton('📢 Broadcast', callback_data='broadcast'),
            types.InlineKeyboardButton('👑 Admin Panel', callback_data='admin_panel'),
            types.InlineKeyboardButton('🟢 Run All Scripts', callback_data='run_all_scripts')
        ]
        markup.add(buttons[0])
        markup.add(buttons[1], buttons[2])
        markup.add(buttons[3], buttons[4])
        markup.add(admin_buttons[0], admin_buttons[1])
        markup.add(admin_buttons[3], admin_buttons[4])
        markup.add(admin_buttons[2], admin_buttons[5])
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
    for row_buttons_text in layout_to_use: markup.add(*[types.KeyboardButton(text) for text in row_buttons_text])
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
    markup.add(types.InlineKeyboardButton("🔙 Back to Files", callback_data='check_files'))
    return markup

def send_main_menu(chat_id, user_id):
    """Helper function to send the main menu (with or without video)"""
    inline_markup = create_main_menu_inline(user_id)
    video_id = get_menu_video_id()
    
    caption_text = "✨ **Welcome to Hosting Bot!** ✨\nChoose an option below to manage your scripts securely."
    
    if video_id:
        bot.send_video(chat_id, video_id, caption=caption_text, reply_markup=inline_markup, parse_mode="Markdown")
    else:
        if user_id in admin_ids:
            caption_text += "\n\n*(Admin Tip: Send any video with the caption `/setvideo` to display a video here!)*"
        bot.send_message(chat_id, caption_text, reply_markup=inline_markup, parse_mode="Markdown")

# --- Admin Command to Set the Video ---
@bot.message_handler(content_types=['video'])
def handle_menu_video_upload(message):
    """Allows the owner/admin to upload a video that will appear in the main menu."""
    user_id = message.from_user.id
    if user_id in admin_ids and message.caption and message.caption.strip().lower() == '/setvideo':
        try:
            save_menu_video_id(message.video.file_id)
            bot.reply_to(message, "✅ Menu video successfully set! It will now appear above the main menu.")
        except Exception as e:
            bot.reply_to(message, f"❌ Failed to set video: {e}")

# --- Automatic Package Installation & Script Running ---
def attempt_install_pip(module_name, message):
    try:
        command = [sys.executable, '-m', 'pip', 'install', module_name]
        subprocess.run(command, capture_output=True, text=True, check=False)
        return True
    except Exception: return False

def run_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply, attempt=1):
    script_key = f"{script_owner_id}_{file_name}"
    try:
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = open(log_file_path, 'w', encoding='utf-8', errors='ignore')
        process = subprocess.Popen([sys.executable, script_path], cwd=user_folder, stdout=log_file, stderr=log_file, stdin=subprocess.PIPE)
        bot_scripts[script_key] = {
            'process': process, 'log_file': log_file, 'file_name': file_name,
            'chat_id': message_obj_for_reply.chat.id, 'script_owner_id': script_owner_id,
            'start_time': datetime.now(), 'user_folder': user_folder, 'type': 'py', 'script_key': script_key
        }
        bot.send_message(message_obj_for_reply.chat.id, f"✅ Script '{file_name}' started! (PID: {process.pid})")
    except Exception as e: bot.send_message(message_obj_for_reply.chat.id, f"❌ Error: {e}")

def run_js_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply, attempt=1):
    script_key = f"{script_owner_id}_{file_name}"
    try:
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = open(log_file_path, 'w', encoding='utf-8', errors='ignore')
        process = subprocess.Popen(['node', script_path], cwd=user_folder, stdout=log_file, stderr=log_file, stdin=subprocess.PIPE)
        bot_scripts[script_key] = {
            'process': process, 'log_file': log_file, 'file_name': file_name,
            'chat_id': message_obj_for_reply.chat.id, 'script_owner_id': script_owner_id,
            'start_time': datetime.now(), 'user_folder': user_folder, 'type': 'js', 'script_key': script_key
        }
        bot.send_message(message_obj_for_reply.chat.id, f"✅ Script '{file_name}' started! (PID: {process.pid})")
    except Exception as e: bot.send_message(message_obj_for_reply.chat.id, f"❌ Error: {e}")

# --- Handlers ---
@bot.message_handler(commands=['start', 'help'])
def command_send_welcome(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if user_id not in active_users:
        active_users.add(user_id)
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('INSERT OR IGNORE INTO active_users (user_id) VALUES (?)', (user_id,))
        conn.commit(); conn.close()

    main_reply_markup = create_reply_keyboard_main_menu(user_id)
    bot.send_message(chat_id, "Generating Hosting Panel...", reply_markup=main_reply_markup)
    send_main_menu(chat_id, user_id)

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
        bot.reply_to(message, f"⚠️ File limit reached.")
        return

    file_name = doc.file_name
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

        file_path = os.path.join(user_folder, file_name)
        with open(file_path, 'wb') as f: f.write(downloaded_file_content)
        
        if file_ext == '.js': 
            save_user_file(user_id, file_name, 'js')
            threading.Thread(target=run_js_script, args=(file_path, user_id, user_folder, file_name, message)).start()
        elif file_ext == '.py': 
            save_user_file(user_id, file_name, 'py')
            threading.Thread(target=run_script, args=(file_path, user_id, user_folder, file_name, message)).start()
    except Exception as e:
        bot.reply_to(message, f"❌ Unexpected error: {str(e)}")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    data = call.data

    # --- Handlers for main menu buttons ---
    if data == 'upload':
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "📤 **Ready for upload!**\nPlease send your `.py`, `.js`, or `.zip` file directly to this chat.", parse_mode="Markdown")
        
    elif data == 'speed':
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "⚡ Bot speed is normal. Server is running smoothly.")
        
    elif data == 'send_command':
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "📤 Command sender feature is active.")
        
    elif data == 'stats':
        bot.answer_callback_query(call.id)
        total_files = sum(len(f) for f in user_files.values())
        bot.send_message(call.message.chat.id, f"📊 **Bot Statistics:**\n\nActive Users: {len(active_users)}\nTotal Hosted Files: {total_files}", parse_mode="Markdown")

    # --- Handlers for Admin buttons ---
    elif data in ['subscription', 'broadcast', 'admin_panel', 'run_all_scripts']:
        bot.answer_callback_query(call.id, "👑 Admin feature is under construction!", show_alert=True)

    elif data == 'lock_bot':
        global bot_locked
        bot_locked = True
        bot.answer_callback_query(call.id, "🔒 Bot is now Locked! Only admins can upload.", show_alert=True)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        send_main_menu(call.message.chat.id, user_id)

    elif data == 'unlock_bot':
        bot_locked = False
        bot.answer_callback_query(call.id, "🔓 Bot Unlocked! Users can upload again.", show_alert=True)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        send_main_menu(call.message.chat.id, user_id)

    # --- File Management Handlers ---
    elif data == 'check_files':
        user_files_list = user_files.get(user_id, [])
        if not user_files_list:
            bot.answer_callback_query(call.id, "⚠️ No files uploaded.", show_alert=True)
            return
        bot.answer_callback_query(call.id) 
        markup = types.InlineKeyboardMarkup(row_width=1) 
        for file_name, file_type in sorted(user_files_list): 
            is_running = is_bot_running(user_id, file_name)
            status_icon = "🟢 Running" if is_running else "🔴 Stopped"
            btn_text = f"{file_name} ({file_type}) - {status_icon}"
            markup.add(types.InlineKeyboardButton(btn_text, callback_data=f'file_{user_id}_{file_name}'))
        markup.add(types.InlineKeyboardButton("🔙 Back to Main", callback_data='back_to_main'))
        
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "📂 **Your files:**", reply_markup=markup, parse_mode="Markdown")
    
    elif data.startswith('file_'):
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        is_running = is_bot_running(script_owner_id, file_name)
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            f"⚙️ Controls for: `{file_name}`\nStatus: {'🟢 Running' if is_running else '🔴 Stopped'}",
            call.message.chat.id, call.message.message_id,
            reply_markup=create_control_buttons(script_owner_id, file_name, is_running), parse_mode='Markdown'
        )

    elif data.startswith('start_'):
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        user_folder = get_user_folder(script_owner_id)
        file_path = os.path.join(user_folder, file_name)
        bot.answer_callback_query(call.id, f"⏳ Starting {file_name}...")
        
        bot.edit_message_text(
            f"⚙️ Controls for: `{file_name}`\nStatus: 🟢 Running",
            call.message.chat.id, call.message.message_id,
            reply_markup=create_control_buttons(script_owner_id_str, file_name, is_running=True), parse_mode='Markdown'
        )

        if file_name.endswith('.py'):
            threading.Thread(target=run_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
        elif file_name.endswith('.js'):
            threading.Thread(target=run_js_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
            
    elif data.startswith('stop_'):
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_key = f"{script_owner_id_str}_{file_name}"
        bot.answer_callback_query(call.id, f"⏳ Stopping {file_name}...")
        if script_key in bot_scripts:
            kill_process_tree(bot_scripts[script_key])
            del bot_scripts[script_key]
            bot.edit_message_text(
                f"⚙️ Controls for: `{file_name}`\nStatus: 🔴 Stopped",
                call.message.chat.id, call.message.message_id,
                reply_markup=create_control_buttons(script_owner_id_str, file_name, is_running=False), parse_mode='Markdown'
            )

    elif data.startswith('delete_'):
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        script_key = f"{script_owner_id_str}_{file_name}"
        
        bot.answer_callback_query(call.id, f"🗑️ Deleting {file_name}...")
        
        # Stop it if it's running
        if script_key in bot_scripts:
            kill_process_tree(bot_scripts[script_key])
            del bot_scripts[script_key]
            
        # Delete from database and file system
        remove_user_file_db(script_owner_id, file_name)
        file_path = os.path.join(get_user_folder(script_owner_id), file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, f"✅ `{file_name}` has been deleted.", parse_mode="Markdown")

    elif data == 'back_to_main':
        bot.answer_callback_query(call.id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        send_main_menu(call.message.chat.id, user_id)

def cleanup():
    for key in list(bot_scripts.keys()):
        kill_process_tree(bot_scripts[key])
atexit.register(cleanup)

if __name__ == '__main__':
    keep_alive()
    logger.info("🚀 Starting polling...")
    while True:
        try: bot.infinity_polling(timeout=60, long_polling_timeout=30)
        except Exception as e: time.sleep(15)
