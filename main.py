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
# ⚙️ SECURE CREDENTIAL LOADER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API_ID = None
API_HASH = None

# Attempt to load from local config.txt file
if os.path.exists("config.txt"):
    with open("config.txt", "r") as f:
        for line in f:
            if line.strip() and "=" in line:
                key, val = line.strip().split("=", 1)
                if key == "API_ID":
                    API_ID = val
                elif key == "API_HASH":
                    API_HASH = val

# Fallback to Environment Variables if hosting on cloud
if not API_ID:
    API_ID = os.environ.get("API_ID")
if not API_HASH:
    API_HASH = os.environ.get("API_HASH")

if not API_ID or not API_HASH:
    print("❌ ERROR: Missing API_ID or API_HASH settings!")
    print("Please make sure they are written inside config.txt or your cloud environment variables.")
    sys.exit(1)

# --- Attractive Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s ⚡ %(message)s', datefmt='%H:%M:%S')

# Initialize client as a real User account
client = TelegramClient('vizard_session', int(API_ID), API_HASH)

# --- Global Variables ---
start_time = time.time()
is_afk = False
afk_reason = ""

# ==========================================
#        ✨ ATTRACTIVE COMMANDS ✨
# ==========================================

@client.on(events.NewMessage(pattern=r'\.alive', outgoing=True))
async def alive_handler(event):
    uptime = round(time.time() - start_time)
    minutes, seconds = divmod(uptime, 60)
    hours, minutes = divmod(minutes, 60)
    uptime_str = f"{hours}h {minutes}m {seconds}s"
    
    alive_msg = (
        "🤖 **V I Z A R D   U S E R B O T** 🤖\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🟢 **Status:** `Systems Online`\n"
        f"⏱️ **Uptime:** `{uptime_str}`\n"
        "🛡️ **Host:** `Production Core Engine`\n"
        "✨ **Version:** `v2.5 Elite`\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "👑 _Ready for your commands, Master._"
    )
    await event.edit(alive_msg)


@client.on(events.NewMessage(pattern=r'\.ping', outgoing=True))
async def ping_handler(event):
    start = time.time()
    msg = await event.edit("🏓 `Pinging server...`")
    end = time.time()
    ping_time = round((end - start) * 1000, 2)
    
    await msg.edit(
        "🏓 **P O N G !**\n"
        "━━━━━━━━━━━━━━\n"
        f"⚡ **Speed:** `{ping_time} ms`\n"
        "━━━━━━━━━━━━━━"
    )


@client.on(events.NewMessage(pattern=r'\.sysinfo', outgoing=True))
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
    await event.edit(sys_msg)


@client.on(events.NewMessage(pattern=r'\.afk (.*)', outgoing=True))
async def set_afk(event):
    global is_afk, afk_reason
    is_afk = True
    afk_reason = event.pattern_match.group(1)
    await event.edit(
        f"🛑 **S E C U R I T Y   A C T I V E** 🛑\n"
        f"User is currently AFK.\n"
        f"📝 **Reason:** `{afk_reason}`"
    )

@client.on(events.NewMessage(pattern=r'\.unafk', outgoing=True))
async def set_unafk(event):
    global is_afk, afk_reason
    if is_afk:
        is_afk = False
        afk_reason = ""
        await event.edit("✅ **User has returned. AFK deactivated.**")


@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def afk_responder(event):
    global is_afk, afk_reason
    if is_afk and not event.text.startswith('.'):
        await event.reply(
            f"🛡️ **Automated Defense System:**\n\n"
            f"The user is currently away from their keyboard.\n"
            f"📝 **Given Reason:** `{afk_reason}`\n\n"
            f"_Please leave your message and they will respond upon return._"
        )


@client.on(events.NewMessage(pattern=r'\.info', outgoing=True))
async def get_info(event):
    if not event.is_reply:
        return await event.edit("⚠️ `Reply to a user's message to get their info.`")
    
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
            f"🔹 **Bot:** `{user.bot}`\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        await event.edit(info_msg)


@client.on(events.NewMessage(pattern=r'\.id', outgoing=True))
async def get_id(event):
    chat_id = event.chat_id
    if event.is_reply:
        replied_msg = await event.get_reply_message()
        user_id = replied_msg.sender_id
        await event.edit(f"🏷️ **Chat ID:** `{chat_id}`\n👤 **User ID:** `{user_id}`")
    else:
        await event.edit(f"🏷️ **Chat ID:** `{chat_id}`")


@client.on(events.NewMessage(pattern=r'\.spam (\d+) (.*)', outgoing=True))
async def spam_handler(event):
    count = int(event.pattern_match.group(1))
    text = event.pattern_match.group(2)
    
    if count > 50:
        return await event.edit("⚠️ `Spam limit is 50 to protect your account.`")
        
    await event.delete()
    for _ in range(count):
        await event.respond(text)
        await asyncio.sleep(0.3)


@client.on(events.NewMessage(pattern=r'\.magic', outgoing=True))
async def magic_animation(event):
    animations = [
        "🕛 `Initiating Magic...`",
        "🕧 `Gathering Mana...`",
        "🕐 `Casting Spell...`",
        "⚡ **V I Z A R D** ⚡",
        "✨ **M A G I C** ✨",
        "🔥 **I S** 🔥",
        "💥 **O V E R P O W E R E D** 💥"
    ]
    for frame in animations:
        try:
            await event.edit(frame)
            await asyncio.sleep(0.5)
        except MessageNotModifiedError:
            pass


@client.on(events.NewMessage(pattern=r'\.del', outgoing=True))
async def delete_msg(event):
    if event.is_reply:
        replied_msg = await event.get_reply_message()
        try:
            await replied_msg.delete()
            await event.delete()
        except Exception as e:
            await event.edit(f"⚠️ `Failed to delete: {str(e)}`")
    else:
        await event.edit("⚠️ `Reply to a message to delete it.`")


if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 VIZARD USERBOT INITIATING...")
    print("="*50 + "\n")
    
    client.start()
    
    print("✅ CONNECTION ESTABLISHED! LISTENING ON TELEGRAM...")
    print("👉 Type .alive in any Telegram chat to verify.")
    client.run_until_disconnected()
