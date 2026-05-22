import os
import sys
import logging
import time
import platform
import psutil
import asyncio
from telethon import TelegramClient, events
from telethon.errors.rpcerrorlist import MessageNotModifiedError

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

# --- Global Variables ---
start_time = time.time()

# ==========================================
#        ✨ ATTRACTIVE BOT COMMANDS ✨
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
        f"💾 **RAM Usage:** `{ram}%`\n"
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


if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 VIZARD BOT CORE ENGINE INITIALIZING...")
    print("="*50 + "\n")
    
    # Clean programmatic startup utilizing the target token directly
    client.start(bot_token=BOT_TOKEN)
    
    print("✅ DEPLOYMENT STABLE! LISTENING FOR INCOMING COMMANDS...")
    client.run_until_disconnected()
