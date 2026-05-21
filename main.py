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
import importlib.util
import asyncio

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

# --- Telethon Component Imports ---
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PasswordHashInvalidError

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
TOKEN = '6248614957:AAGWzd37KASqv6u3OZRxt3gPaqkkdpmRNHg' 
OWNER_ID = 2119464081
ADMIN_ID = 2119464081
YOUR_USERNAME = '@Xricx0' 
UPDATE_CHANNEL = 'https://t.me/+5uCnxp3U1gMwZjQ1'

# Global memory registry to track active Telethon setup contexts
runtime_states = {}
# Active asyncio loops per user thread
async_loops = {}

# Folder setup - using absolute paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_BOTS_DIR = os.path.join(BASE_DIR, "uploaded_bots")
IROTECH_DIR = os.path.join(BASE_DIR, "irotech_data")
os.makedirs(UPLOAD_BOTS_DIR, exist_ok=True)
os.makedirs(IROTECH_DIR, exist_ok=True)

bot = telebot.TeleBot(TOKEN)
admin_ids = [OWNER_ID, ADMIN_ID]

# Helper Regex to automatically find API_ID and API_HASH constants inside files
def extract_credentials_from_text(text):
    api_id, api_hash = None, None
    id_match = re.search(r'(?:API_ID)\s*=\s*[\'"]?(\d+)[\'"]?', text, re.IGNORECASE)
    hash_match = re.search(r'(?:API_HASH)\s*=\s*[\'"]?([a-fA-Z0-9a-f]{32})[\'"]?', text, re.IGNORECASE)
    if id_match: api_id = id_match.group(1)
    if hash_match: api_hash = hash_match.group(1)
    return api_id, api_hash


# --- Asyncio Runtime Core Executor Wrapper ---
def start_asyncio_loop(loop, coro):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)


# --- Custom Userbot Dynamic Runtime Processor ---
async def deploy_custom_runtime(chat_id, uid, state):
    script_path = state["script_path"]
    user_api_id = state["api_id"]
    user_api_hash = state["api_hash"]
    
    bot.send_message(chat_id, "🛡️ **Signature Validated.** Merging dynamic runtime into master async event loop...")
    await state["client"].disconnect()
    
    old_session = f"auth_temp_{uid}.session"
    new_session = f"user_session_{uid}"
    
    if os.path.exists(old_session):
        if os.path.exists(f"{new_session}.session"): 
            os.remove(f"{new_session}.session")
        os.rename(old_session, new_session + ".session")
        
    try:
        # Re-initialize user bot instance loop
        live_userbot = TelegramClient(new_session, int(user_api_id), user_api_hash)
        await live_userbot.connect()
        
        spec = importlib.util.spec_from_file_location(f"dynamic_mod_{uid}", script_path)
        user_module = importlib.util.module_from_spec(spec)
        user_module.client = live_userbot 
        spec.loader.exec_module(user_module)
        
        # Keep engine connected and listening
        asyncio.create_task(live_userbot.start())
        
        success_message = f"""🚀 **DYNAMIC USERBOT RUNTIME ONLINE** 🚀
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ **System Status:** `RUNNING`
📂 **Active Package Target:** `{os.path.basename(script_path)}`
🔐 **Session Allocation ID:** `{new_session}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌟 **Deployment Finished!** Your userbot events have been hot-plugged directly into the engine room successfully."""
        bot.send_message(chat_id, success_message)
        
    except Exception as e:
        bot.send_message(chat_id, f"❌ **Process Core Allocation Fault:** Cloud memory injection failed: `{e}`")
    
    if uid in runtime_states: 
        del runtime_states[uid]


# --- Telebot Step-By-Step Setup Integration Router ---
@bot.message_handler(commands=['setup_userbot'])
def setup_userbot_cmd(message):
    uid = message.from_user.id
    runtime_states[uid] = {"step": "AWAITING_SCRIPT"}
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ Cancel Process", callback_data="cancel_userbot_setup"))
    
    welcome_text = """✨ **Welcome to the Userbot Setup Wizard** ✨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This wizard will register and host your custom Telethon script.

🔮 **CURRENT STAGE:** `[◯] 🛠️ Step 1 / 3` 
👉 **Action Required:** Please upload your userbot script file (`.py`)."""
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)


@bot.message_handler(content_types=['document'])
def handle_userbot_document(message):
    uid = message.from_user.id
    if uid not in runtime_states or runtime_states[uid]["step"] != "AWAITING_SCRIPT":
        # Fallback to standard tracking file parsing from your original script asset
        return 

    if message.document.file_name.endswith('.py'):
        bot.send_message(message.chat.id, "📥 **Analyzing file layout and downloading sources...**")
        
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        target_filename = os.path.join(UPLOAD_BOTS_DIR, f"userbot_{uid}.py")
        with open(target_filename, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        runtime_states[uid]["script_path"] = target_filename
        
        try:
            with open(target_filename, 'r', encoding='utf-8', errors='ignore') as f:
                script_content = f.read()
            api_id, api_hash = extract_credentials_from_text(script_content)
            
            if not api_id or not api_hash:
                caption_text = message.caption or ""
                api_id, api_hash = extract_credentials_from_text(caption_text)
                
            if api_id and api_hash:
                runtime_states[uid]["api_id"] = api_id
                runtime_states[uid]["api_hash"] = api_hash
                runtime_states[uid]["step"] = "PHONE"
                
                msg = f"✅ **Script Autoparsed!**\n⚡ **Instance API ID:** `{api_id}`\n\n🔮 **STAGE 2:** Provide the phone number linked to this Telegram account (e.g. `+1234567890`):"
                bot.send_message(message.chat.id, msg)
            else:
                if os.path.exists(target_filename): os.remove(target_filename)
                bot.send_message(message.chat.id, "❌ **Auto-Extraction Failed:** Could not locate `API_ID` or `API_HASH` inside the `.py` source file text layout.")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ **Error compilation context:** `{e}`")
    else:
        bot.send_message(message.chat.id, "❌ Please upload a valid Python (`.py`) script.")


@bot.message_handler(func=lambda message: True)
def handle_text_wizard_pipeline(message):
    uid = message.from_user.id
    if uid not in runtime_states:
        return # Drop out to standard handlers if user isn't configuring userbots

    state = runtime_states[uid]
    text = message.text.strip()

    if state["step"] == "PHONE":
        if not text.startswith('+') or not text[1:].isdigit():
            bot.send_message(message.chat.id, "❌ **Format Error:** Enter text parameters matching formatting structures exactly (`+XXXXXXXXXXX`).")
            return
        
        state["phone"] = text
        bot.send_message(message.chat.id, "⏳ **Negotiating secure authorization wrapper...**")
        
        # Isolate Async Engine operations into structural runtime pools
        new_loop = asyncio.new_event_loop()
        async_loops[uid] = new_loop
        
        temp_session = f"auth_temp_{uid}"
        client = TelegramClient(temp_session, int(state["api_id"]), state["api_hash"], loop=new_loop)
        
        async def connect_and_request_code():
            await client.connect()
            send_code = await client.send_code_request(text)
            state["client"] = client
            state["phone_code_hash"] = send_code.phone_code_hash
            state["step"] = "OTP"
            bot.send_message(message.chat.id, "📩 **Verification Token Dispatched!** Reply with your Login Code/OTP below:")

        t = Thread(target=start_asyncio_loop, args=(new_loop, connect_and_request_code()))
        t.start()

    elif state["step"] == "OTP":
        client = state["client"]
        otp_code = text.replace(" ", "")
        bot.send_message(message.chat.id, "🔐 **Validating verification signature...**")
        
        async def sign_in_otp():
            try:
                await client.sign_in(phone=state["phone"], code=otp_code, phone_code_hash=state["phone_code_hash"])
                await deploy_custom_runtime(message.chat.id, uid, state)
            except PhoneCodeInvalidError:
                bot.send_message(message.chat.id, "❌ **Incorrect Code.** Try providing your updated code string:")
            except SessionPasswordNeededError:
                state["step"] = "2FA"
                bot.send_message(message.chat.id, "🔒 **2FA Protection Active.** Please respond with your account password:")
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ **Handshake Aborted:** `{e}`")
                await client.disconnect()
                del runtime_states[uid]

        t = Thread(target=start_asyncio_loop, args=(async_loops[uid], sign_in_otp()))
        t.start()

    elif state["step"] == "2FA":
        client = state["client"]
        
        async def sign_in_2fa():
            try:
                await client.sign_in(password=text)
                await deploy_custom_runtime(message.chat.id, uid, state)
            except PasswordHashInvalidError:
                bot.send_message(message.chat.id, "❌ **Password Verification Failed.** Type again:")
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ **System Error:** `{e}`")
                await client.disconnect()
                del runtime_states[uid]

        t = Thread(target=start_asyncio_loop, args=(async_loops[uid], sign_in_2fa()))
        t.start()


@bot.callback_query_handler(func=lambda call: call.data == "cancel_userbot_setup")
def cancel_userbot_callback(call):
    uid = call.from_user.id
    if uid in runtime_states:
        del runtime_states[uid]
    bot.edit_message_text("⚠️ **Userbot Setup Wizard Cancelled.**", call.message.chat.id, call.message.message_id)


# --- Original Process Tree Management Cleanup ---
def kill_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True): child.kill()
        parent.kill()
    except psutil.NoSuchProcess: pass

# --- Main Execution ---
if __name__ == '__main__':
    logger.info("="*40 + "\n🤖 Bot Starting Up...\n" + "="*40)
    keep_alive()
    logger.info("🚀 Starting telebot polling engine...")
    while True:
        try:
            bot.infinity_polling(logger_level=logging.INFO, timeout=60, long_polling_timeout=30)
        except Exception as e:
            logger.error(f"Polling Exception: {e}")
            time.sleep(5)
