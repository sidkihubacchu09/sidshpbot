import asyncio
import os
import subprocess
import sys
import logging
import re
from aiohttp import web
from telethon import TelegramClient, events, Button
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PasswordHashInvalidError

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# HOSTING BOT CREDENTIALS
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
MANAGER_API_ID = int(os.getenv("MANAGER_API_ID", "1234567"))
MANAGER_API_HASH = os.getenv("MANAGER_API_HASH", "your_manager_api_hash_here")

runtime_states = {}
manager_bot = TelegramClient('dynamic_manager_session', MANAGER_API_ID, MANAGER_API_HASH)
CANCEL_BTN = [Button.inline("❌ Cancel Setup Process", b"cancel_deployment")]

def extract_credentials_from_text(text):
    api_id, api_hash = None, None
    id_match = re.search(r'(?:API_ID)\s*=\s*[\'"]?(\d+)[\'"]?', text, re.IGNORECASE)
    hash_match = re.search(r'(?:API_HASH)\s*=\s*[\'"]?([a-fA-Z0-9a-f]{32})[\'"]?', text, re.IGNORECASE)
    if id_match: api_id = id_match.group(1)
    if hash_match: api_hash = hash_match.group(1)
    return api_id, api_hash

# --- WEB SERVER HANDLERS ---
async def handle_index(request):
    """Serves the index.html Web App dashboard file when the URL is accessed."""
    try:
        return web.FileResponse('./index.html')
    except FileNotFoundError:
        return web.Response(text="index.html not found in project root folder.", status=404)

# --- TELEGRAM BOT EVENT LOGIC ---
@manager_bot.on(events.NewMessage(pattern='/start'))
async def start_cmd(event):
    uid = event.sender_id
    runtime_states[uid] = {"step": "AWAITING_SCRIPT"}
    
    welcome_text = """✨ **Welcome to the Sid Userbot Platform** ✨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This automated setup wizard will provision an isolated, \
background sandbox container to host your script 24/7.

🔮 **CURRENT STAGE:** `[◯] 🛠️ Step 1 / 3` 
👉 **Action Required:** Please upload your custom userbot script file (`.py`)."""
    
    await event.reply(welcome_text, buttons=CANCEL_BTN)

@manager_bot.on(events.CallbackQuery(data=b"cancel_deployment"))
async def cancel_callback(event):
    uid = event.sender_id
    if uid in runtime_states:
        if "client" in runtime_states[uid]:
            try: await runtime_states[uid]["client"].disconnect()
            except Exception: pass
        del runtime_states[uid]
    await event.edit("⚠️ **Setup Wizard Terminated**")

@manager_bot.on(events.NewMessage)
async def dynamic_hosting_router(event):
    uid = event.sender_id
    text = event.text.strip() if event.text else ""
    if (text.startswith('/') and text != '/start') or uid not in runtime_states or text == '/start':
        return
    
    state = runtime_states[uid]

    if state["step"] == "AWAITING_SCRIPT":
        if event.message.document and event.message.file.ext == '.py':
            await event.reply("📥 **Analyzing file layout and downloading sources...**")
            target_filename = f"userbot_{uid}.py"
            path = await event.message.download_media(file=target_filename)
            state["script_path"] = path
            
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    script_content = f.read()
                api_id, api_hash = extract_credentials_from_text(script_content)
                
                if not api_id or not api_hash:
                    caption_text = event.message.message or ""
                    api_id, api_hash = extract_credentials_from_text(caption_text)
                
                if api_id and api_hash:
                    state["api_id"] = api_id
                    state["api_hash"] = api_hash
                    state["step"] = "PHONE"
                    
                    msg = f"✅ **Script Autoparsed!**\n⚡ **Instance API ID:** `{api_id}`\n\n👉 Reply with your phone number (`+1234567890`):"
                    await event.reply(msg, buttons=CANCEL_BTN)
                else:
                    if os.path.exists(path): os.remove(path)
                    await event.reply("❌ **Auto-Extraction Failed:** Make sure API_ID and API_HASH are defined in the script.")
            except Exception as e:
                await event.reply(f"❌ **Error reading file:** `{e}`")
        return

    elif state["step"] == "PHONE":
        if not text.startswith('+') or not text[1:].isdigit():
            await event.reply("❌ **Format Error:** Enter number using `+XXXXXXXXXXX` rules.")
            return
        state["phone"] = text
        await event.reply("⏳ **Negotiating secure verification session...**")
        temp_session = f"auth_temp_{uid}"
        client = TelegramClient(temp_session, int(state["api_id"]), state["api_hash"])
        await client.connect()
        try:
            send_code = await client.send_code_request(text)
            state["client"] = client
            state["phone_code_hash"] = send_code.phone_code_hash
            state["step"] = "OTP"
            await event.reply("📩 **OTP Token Sent!** Reply with your code below:", buttons=CANCEL_BTN)
        except Exception as e:
            await event.reply(f"❌ **Handshake Aborted:** `{e}`")
            await client.disconnect()
            del runtime_states[uid]

    elif state["step"] == "OTP":
        client = state["client"]
        await event.reply("🔐 **Validating authorization matrix...**")
        try:
            await client.sign_in(phone=state["phone"], code=text.replace(" ", ""), phone_code_hash=state["phone_code_hash"])
            await deploy_custom_runtime(event, uid, state)
        except PhoneCodeInvalidError:
            await event.reply("❌ Code incorrect. Try again:")
        except SessionPasswordNeededError:
            state["step"] = "2FA"
            await event.reply("🔒 **2FA Protection Active.** Reply with your account password:", buttons=CANCEL_BTN)
        except Exception as e:
            await event.reply(f"❌ **Fault:** `{e}`")
            await client.disconnect()
            del runtime_states[uid]

    elif state["step"] == "2FA":
        client = state["client"]
        try:
            await client.sign_in(password=text)
            await deploy_custom_runtime(event, uid, state)
        except PasswordHashInvalidError:
            await event.reply("❌ Password incorrect. Try again:")
        except Exception as e:
            await event.reply(f"❌ **Error:** `{e}`")
            await client.disconnect()
            del runtime_states[uid]

async def deploy_custom_runtime(event, uid, state):
    client = state["client"]
    script_path = state["script_path"]
    user_api_id = state["api_id"]
    user_api_hash = state["api_hash"]
    await event.reply("🛡️ **Signature Validated.** Starting isolated core thread...")
    await client.disconnect()
    
    old_session = f"auth_temp_{uid}.session"
    new_session = f"user_session_{uid}"
    if os.path.exists(old_session):
        if os.path.exists(f"{new_session}.session"): os.remove(f"{new_session}.session")
        os.rename(old_session, new_session + ".session")
        
    try:
        subprocess.Popen(
            [sys.executable, script_path, new_session, str(user_api_id), user_api_hash, str(uid)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        await event.reply("🚀 **DYNAMIC DAEMON RUNTIME ONLINE** 🚀")
    except Exception as e:
        await event.reply(f"❌ Core allocation failed: `{e}`")
    if uid in runtime_states: del runtime_states[uid]

# --- MAIN ASYNC ENGINE LOOP ---
async def main():
    # Start Telegram Client
    await manager_bot.start(bot_token=BOT_TOKEN)
    
    # Configure Web Server Layer
    app = web.Application()
    app.router.add_get('/', handle_index)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Pull dynamic port assigned by Railway
    port = int(os.getenv("PORT", "8080"))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logging.info(f"Web application layer active on port {port}")
    await manager_bot.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
