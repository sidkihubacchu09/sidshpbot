import os
import sys
import logging
import time
import platform
import psutil
import asyncio
from telethon import TelegramClient, events
from telethon.errors.rpcerrorlist import MessageNotModifiedError

# Web App imports
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚙️ SECURE CREDENTIAL LOADER (Railway Dashboard)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Fallback values for local testing if cloud variables aren't active yet
if not API_ID or not API_HASH or not BOT_TOKEN:
    API_ID = "38843772"
    API_HASH = "875fbb273801c8025d05e98173fca536"
    BOT_TOKEN = "8212227179:AAHiwdROhqHUU9cYdQ6NvOVKo8eGi8LO9bk"

# --- Attractive Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s ⚡ %(message)s', datefmt='%H:%M:%S')

# Initialize client cleanly as a Telegram Bot Engine
client = TelegramClient('vizard_bot_session', int(API_ID), API_HASH)

# Initialize FastAPI App
app = FastAPI(title="Vizard Bot Dashboard")

# --- Global Variables ---
start_time = time.time()

# ==========================================
#         🌐 WEB APPLICATION LAYER
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    uptime = round(time.time() - start_time)
    minutes, seconds = divmod(uptime, 60)
    hours, minutes = divmod(minutes, 60)
    uptime_str = f"{hours}h {minutes}m {seconds}s"
    
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    
    # Modern dark-mode HTML dashboard
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Vizard Bot Dashboard</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #0e1118;
                color: #ffffff;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }}
            .card {{
                background: #161b26;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.5);
                border: 1px solid #232d3f;
                max-width: 400px;
                width: 100%;
                text-align: center;
            }}
            h1 {{ color: #00e676; margin-bottom: 5px; font-size: 24px; letter-spacing: 2px; }}
            .subtitle {{ color: #8a99ad; font-size: 14px; margin-bottom: 25px; }}
            .metric {{
                display: flex;
                justify-content: space-between;
                padding: 12px 0;
                border-bottom: 1px solid #232d3f;
            }}
            .metric:last-child {{ border: none; }}
            .label {{ color: #8a99ad; font-weight: 500; }}
            .value {{ font-family: 'Courier New', Courier, monospace; color: #00b0ff; font-weight: bold; }}
            .status-online {{ color: #00e676; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🤖 VIZARD BOT </h1>
            <div class="subtitle">Production Control Panel</div>
            <div class="metric">
                <span class="label">Status:</span>
                <span class="value status-online">Systems Online</span>
            </div>
            <div class="metric">
                <span class="label">Uptime:</span>
                <span class="value">{uptime_str}</span>
            </div>
            <div class="metric">
                <span class="label">CPU Load:</span>
                <span class="value">{cpu}%</span>
            </div>
            <div class="metric">
                <span class="label">RAM Usage:</span>
                <span class="value">{ram}%</span>
            </div>
            <div class="metric">
                <span class="label">Environment:</span>
                <span class="value">{platform.system()}</span>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "bot_connected": client.is_connected()}


# ==========================================
#       ✨ ATTRACTIVE BOT COMMANDS ✨
# ==========================================

# 1. ALIVE: Visual status check
@client.on(events.NewMessage(pattern=r'\.alive', incoming=True))
async def alive_handler(event):
    uptime = round(time.time() - start_time)
    minutes, seconds = divmod(uptime, 60)
    hours, minutes = divmod(minutes, 60)
    uptime_str = f"{hours}h {minutes}m {seconds}s"
    
    alive_msg = (
        "🤖 **V I Z A R D   B O T** 🤖\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🟢 **Status:** `Systems Online`\n"
        f"⏱️ **Uptime:** `{uptime_str}`\n"
        "🛡️ **Host:** `Railway Production Engine`\n"
        "✨ **Version:** `v3.0 Bot-Core`\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "👑 _Ready for your commands, Master._"
    )
    await event.respond(alive_msg)


# 2. PING: Response efficiency check
@client.on(events.NewMessage(pattern=r'\.ping', incoming=True))
async def ping_handler(event):
    start = time.time()
    msg = await event.respond("🏓 `Pinging server...`")
    end = time.time()
    ping_time = round((end - start) * 1000, 2)
    
    await msg.edit(
        "🏓 **P O N G !**\n"
        "━━━━━━━━━━━━━━\n"
        f"⚡ **Speed:** `{ping_time} ms`\n"
        "━━━━━━━━━━━━━━"
    )


# 3. SYSINFO: Hosting hardware performance metrics
@client.on(events.NewMessage(pattern=r'\.sysinfo', incoming=True))
async def sysinfo_handler(event):
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    os_name = platform.system()
    
    sys_msg = (
        "🖥️ **S Y S T E M   I N F O R M A T I O N** 🖥️\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚙️ **CPU Usage:** `{cpu}%`\n"
        "💾 **RAM Usage:** `{ram}%`\n"
        f"💿 **OS:** `{os_name}`\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )
    await event.respond(sys_msg)


# 4. INFO: Extract demographic profile details of a user
@client.on(events.NewMessage(pattern=r'\.info', incoming=True))
async def get_info(event):
    if not event.is_reply:
        return await event.respond("⚠️ `Reply to a user's message to target their info.`")
    
    replied_msg = await event.get_reply_message()
    user = await replied_msg.get_sender()
    
    if user:
        info_msg = (
            "👤 **U S E R   I N F O** 👤\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🔹 **First Name:** `{user.first_name}`\n"
            f"🔹 **Last Name:** `{user.last_name or 'None'}`\n"
            f"🔹 **Username:** `@{user.username or 'None'}`\n"
            f"🔹 **User ID:** `{user.id}`\n"
            f"🔹 **Bot Check:** `{user.bot}`\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        await event.respond(info_msg)


# 5. ID: Fetch functional space routing indexes
@client.on(events.NewMessage(pattern=r'\.id', incoming=True))
async def get_id(event):
    chat_id = event.chat_id
    if event.is_reply:
        replied_msg = await event.get_reply_message()
        user_id = replied_msg.sender_id
        await event.respond(f"🏷️ **Chat ID:** `{chat_id}`\n👤 **User ID:** `{user_id}`")
    else:
        await event.respond(f"🏷️ **Chat ID:** `{chat_id}`")


# 6. SPAM: Managed rate transmission loop
@client.on(events.NewMessage(pattern=r'\.spam (\d+) (.*)', incoming=True))
async def spam_handler(event):
    count = int(event.pattern_match.group(1))
    text = event.pattern_match.group(2)
    
    if count > 30:
        return await event.respond("⚠️ `Spam limit capped at 30 to bypass Telegram structural blocks.`")
        
    for _ in range(count):
        await event.respond(text)
        await asyncio.sleep(0.4)


# 7. MAGIC: Matrix mutation design sequence
@client.on(events.NewMessage(pattern=r'\.magic', incoming=True))
async def magic_animation(event):
    msg = await event.respond("🕛 `Initiating Magic...`")
    animations = [
        "🕧 `Gathering Mana...`",
        "💡 `Casting Spell...`",
        "⚡ **V I Z A R D** ⚡",
        "✨ **M A G I C** ✨",
        "💥 **O V E R P O W E R E D** 💥"
    ]
    for frame in animations:
        try:
            await msg.edit(frame)
            await asyncio.sleep(0.5)
        except MessageNotModifiedError:
            pass


# ==========================================
#        🚀 DUAL-ENGINE LIFECYCLE 🚀
# ==========================================

@app.on_event("startup")
async def startup_event():
    print("\n" + "="*50)
    print("🚀 VIZARD BOT CORE ENGINE INITIALIZING...")
    print("="*50 + "\n")
    
    # Start the Telethon client asynchronously within the web framework's event loop
    await client.start(bot_token=BOT_TOKEN)
    print("✅ TELEGRAM CLIENT STABLE & LISTENING...")

@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 DISCONNECTING VIZARD BOT...")
    await client.disconnect()

if __name__ == '__main__':
    # Grab the port injected by cloud hosts (Railway defaults to 5000 if local fallback)
    port = int(os.environ.get("PORT", 5000))
    
    print("✅ DEPLOYMENT STABLE! SPINNING UP WEB APP WEB SERVER...")
    # Run the Uvicorn Web Server
    uvicorn.run("main.py:app", host="0.0.0.0", port=port, reload=False)
