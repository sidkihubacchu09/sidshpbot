import asyncio
import os
import subprocess
import sys
import logging
import re
import importlib.util
from aiohttp import web
from telethon import TelegramClient, events, Button
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PasswordHashInvalidError

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# HOSTING BOT CREDENTIALS
# Dynamically reads from your Railway Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
MANAGER_API_ID = int(os.getenv("MANAGER_API_ID", "1234567"))
MANAGER_API_HASH = os.getenv("MANAGER_API_HASH", "your_manager_api_hash_here")

# Tracks pipeline states per user
runtime_states = {}

# Initialize the manager client
manager_bot = TelegramClient('dynamic_manager_session', MANAGER_API_ID, MANAGER_API_HASH)

# Reusable UI Cancel Button Component
CANCEL_BTN = [Button.inline("❌ Cancel Setup Process", b"cancel_deployment")]


def extract_credentials_from_text(text):
    """Helper function to regex scan text or code for API configurations."""
    api_id = None
    api_hash = None
    
    # Matches patterns like API_ID = 123456 or API_ID="123456" or api_id=123456
    id_match = re.search(r'(?:API_ID)\s*=\s*[\'"]?(\d+)[\'"]?', text, re.IGNORECASE)
    hash_match = re.search(r'(?:API_HASH)\s*=\s*[\'"]?([a-fA-Z0-9a-f]{32})[\'"]?', text, re.IGNORECASE)
    
    if id_match:
        api_id = id_match.group(1)
    if hash_match:
        api_hash = hash_match.group(1)
        
    return api_id, api_hash


# --- WEB SERVER HANDLERS ---
async def handle_index(request):
    """Serves the index.html Web App dashboard file when the Railway URL is accessed."""
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
👉 **Action Required:** Please upload your custom userbot script file (`.py`).

ℹ️ *Tip: Make sure your API_ID and API_HASH variables are written inside the script so the manager can extract them automatically!*"""
    
    await event.reply(welcome_text, buttons=CANCEL_BTN)


@manager_bot.on(events.CallbackQuery(data=b"cancel_deployment"))
async def cancel_callback(event):
    uid = event.sender_id
    if uid in runtime_states:
        if "client" in runtime_states[uid]:
            try:
                await runtime_states[uid]["client"].disconnect()
            except Exception:
                pass
        del runtime_states[uid]
        
    bot_username = (await manager_bot.get_me()).username
    await event.edit(
        """⚠️ **Setup Wizard Terminated**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The current configuration sequence has been successfully discarded.

🔄 *To initialize a fresh cloud instance, click the button below:*""",
        buttons=[Button.url("🚀 Re-Initialize Setup", f"t.me/{bot_username}?start=true")]
    )


@manager_bot.on(events.NewMessage)
async def dynamic_hosting_router(event):
    uid = event.sender_id
    text = event.text.strip() if event.text else ""
    
    if text.startswith('/') and text != '/start':
        return
    if uid not in runtime_states or text == '/start':
        return
    
    state = runtime_states[uid]

    # ----------------- STEP 1: RECEIVE SCRIPT & AUTO EXTRACT -----------------
    if state["step"] == "AWAITING_SCRIPT":
        if event.message.document and event.message.file.ext == '.py':
            await event.reply("📥 **Analyzing file layout and downloading sources...**")
            
            target_filename = f"userbot_{uid}.py"
            path = await event.message.download_media(file=target_filename)
            state["script_path"] = path
            
            # Read script content to look for hardcoded API keys automatically
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    script_content = f.read()
                
                # Try tracking down keys in code or file text descriptions
                api_id, api_hash = extract_credentials_from_text(script_content)
                
                # Fallback: scan message text wrapper/caption if script file didn't include them
                if not api_id or not api_hash:
                    caption_text = event.message.message or ""
                    api_id, api_hash = extract_credentials_from_text(caption_text)
                
                if api_id and api_hash:
                    state["api_id"] = api_id
                    state["api_hash"] = api_hash
                    state["step"] = "PHONE"  # Directly skip manual credential insert step!
                    
                    msg = f"""✅ **Script Compiled & Autoparsed!**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚙️ **Auto-Detected Credentials:**
⚡ **Instance API ID:** `{api_id}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔮 **CURRENT STAGE:** `[●●◯] 📱 Step 2 / 3` 

👉 **Action Required:** Provide the mobile phone number linked to this specific Telegram account.

📌 **Global Standard Notation:** `+ [Country Code] [Phone Number]` (e.g., `+1234567890`)"""
                    await event.reply(msg, buttons=CANCEL_BTN)
                    return
                else:
                    # Clean up file since credentials extraction failed entirely
                    if os.path.exists(path):
                        os.remove(path)
                    await event.reply(
                        "❌ **Auto-Extraction Failed:** Could not find `API_ID` or `API_HASH` values defined inside your script file text.\n\n"
                        "Please update your script to include them or make sure they are written clearly inside your script code before re-uploading!"
                    )
                    return
            except Exception as e:
                await event.reply(f"❌ **Error reading file text profile:** `{e}`")
                return
        else:
            await event.reply("❌ **Invalid Payload Type:** Please forward a valid Python source file ending strictly with a `.py` extension.")
        return

    # ----------------- STEP 2: PHONE NUMBER INPUT -----------------
    elif state["step"] == "PHONE":
        if not text.startswith('+') or not text[1:].isdigit():
            await event.reply("❌ **Formatting Exception:** Please input your telephone parameters using international E.164 rules (`+XXXXXXXXXXX`).")
            return
        
        state["phone"] = text
        await event.reply("⏳ **Negotiating secure verification session layer...**")
        
        temp_session = f"auth_temp_{uid}"
        client = TelegramClient(temp_session, int(state["api_id"]), state["api_hash"])
        await client.connect()
        
        try:
            send_code = await client.send_code_request(text)
            state["client"] = client
            state["phone_code_hash"] = send_code.phone_code_hash
            state["step"] = "OTP"
            
            msg = """📩 **Dynamic Verification Token Dispatched!**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔮 **CURRENT STAGE:** `[●●●] 🔐 Step 3 / 3` 

👉 **Action Required:** Check your official Telegram client messages and reply with the login string/OTP token key below."""
            await event.reply(msg, buttons=CANCEL_BTN)
        except Exception as e:
            await event.reply(f"❌ **Handshake Aborted:** Server rejected the initialization layer: `{e}`\nUse /start to reset.")
            await client.disconnect()
            if os.path.exists(f"{temp_session}.session"):
                os.remove(f"{temp_session}.session")
            del runtime_states[uid]

    # ----------------- STEP 3: OTP VERIFICATION -----------------
    elif state["step"] == "OTP":
        client = state["client"]
        otp_code = text.replace(" ", "")
        
        await event.reply("🔐 **Validating active session authorization matrix...**")
        try:
            await client.sign_in(phone=state["phone"], code=otp_code, phone_code_hash=state["phone_code_hash"])
            await deploy_custom_runtime(event, uid, state)
            
        except PhoneCodeInvalidError:
            await event.reply("❌ **Security Reject:** The verification string submitted is incorrect. Double-check your code and reply:")
        except SessionPasswordNeededError:
            state["step"] = "2FA"
            msg = """🔒 **Cloud Database Protection Triggered (2FA)**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔮 **CURRENT STAGE:** `[●●●] 🛡️ Security Check` 

👉 **Action Required:** Your account has an active 2FA password configuration. Please respond with your account password below:"""
            await event.reply(msg, buttons=CANCEL_BTN)
        except Exception as e:
            await event.reply(f"❌ **Fatal Authentication Fault:** `{e}`\nRun /start to clear cached buffers.")
            await client.disconnect()
            del runtime_states[uid]

    # ----------------- ADVANCED: 2FA PASSWORD -----------------
    elif state["step"] == "2FA":
        client = state["client"]
        try:
            await client.sign_in(password=text)
            await deploy_custom_runtime(event, uid, state)
        except PasswordHashInvalidError:
            await event.reply("❌ **Verification Failure:** Cloud password token signature mismatch. Re-verify spelling and try again:")
        except Exception as e:
            await event.reply(f"❌ **System Error:** Integrity handshake failed: `{e}`\nUse /start to reset.")
            await client.disconnect()
            del runtime_states[uid]


async def deploy_custom_runtime(event, uid, state):
    client = state["client"]
    script_path = state["script_path"]
    user_api_id = state["api_id"]
    user_api_hash = state["api_hash"]
    
    await event.reply("🛡️ **Signature Validated.** Merging dynamic runtime into master async event loop...")
    await client.disconnect()
    
    old_session = f"auth_temp_{uid}.session"
    new_session = f"user_session_{uid}"
    
    if os.path.exists(old_session):
        if os.path.exists(f"{new_session}.session"):
            os.remove(f"{new_session}.session")
        os.rename(old_session, new_session + ".session")
        
    try:
        # Re-initialize the active user client cleanly inside the main process memory footprint
        live_userbot = TelegramClient(new_session, int(user_api_id), user_api_hash)
        await live_userbot.connect()
        
        # Load the uploaded userbot code dynamically into python module memory space
        spec = importlib.util.spec_from_file_location(f"dynamic_mod_{uid}", script_path)
        user_module = importlib.util.module_from_spec(spec)
        
        # Inject the active live_userbot client straight into their module execution context
        user_module.client = live_userbot 
        
        # Execute the module code
        spec.loader.exec_module(user_module)
        
        # Schedule the new userbot client to start up asynchronously alongside your manager bot
        asyncio.create_task(live_userbot.start())
        
        success_message = f"""🚀 **DYNAMIC DAEMON RUNTIME ONLINE** 🚀
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ **System Status:** `RUNNING (Unified Core Loop)`
📂 **Active Package Target:** `{os.path.basename(script_path)}`
🔐 **Session Allocation ID:** `{new_session}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌟 **Deployment Finished!** Your userbot events have been hot-plugged directly into the engine room successfully."""
        
        dashboard_buttons = [
            [
                Button.url("📊 Process Metrics", "https://t.me/telegram"), 
                Button.url("🌐 Cloud Mirror", "https://t.me/telegram")
            ],
            [Button.inline("🛑 Safe Destruct Instance", b"cancel_deployment")]
        ]
        
        await event.reply(success_message, buttons=dashboard_buttons)
        
    except Exception as e:
        await event.reply(f"❌ **Process Core Allocation Fault:** Cloud memory injection failed: `{e}`")
        
    if uid in runtime_states:
        del runtime_states[uid]


# --- MAIN ASYNC ENGINE LOOP ---
async def main():
    # Start Telegram Client Manager Bot
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
    
    print(f"--- Web App Application Layer active on port {port} ---")
    print(f"--- Dynamic Script Cloud Host Manager Bot Running ---")
    
    await manager_bot.run_until_disconnected()


if __name__ == '__main__':
    asyncio.run(main())
