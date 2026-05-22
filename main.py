import sys
import logging
import time
import platform
import psutil
from telethon import TelegramClient, events

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚙️ CREDENTIALS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API_ID = "YOUR_API_ID" 
API_HASH = "YOUR_API_HASH"
BOT_TOKEN = "8637135798:AAEdTzCnL3fn1keuLzLxQN0BUULXlTMicVY"

# --- Attractive Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s ⚡ %(message)s', datefmt='%H:%M:%S')

# --- Host Bot Integration ---
if len(sys.argv) > 1:
    session_name = sys.argv[1] 
    api_id = int(sys.argv[2])
    api_hash = sys.argv[3]
else:
    session_name = 'local_session'
    api_id = int(API_ID) if API_ID.isdigit() else 0
    api_hash = API_HASH

client = TelegramClient(session_name, api_id, api_hash)

# --- Global Variables ---
start_time = time.time()
is_afk = False
afk_reason = ""

# ==========================================
#        ✨ ATTRACTIVE COMMANDS ✨
# ==========================================

# 1. ALIVE: A beautiful status message
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
        "🛡️ **Host:** `Railway Premium Engine`\n"
        "✨ **Version:** `v2.0 Elite`\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "👑 _Ready for your commands, Master._"
    )
    await event.respond(alive_msg)


# 2. SYSINFO: Check your server's hardware stats
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
    await event.respond(sys_msg)


# 3. AFK MODE: Stylish away status
@client.on(events.NewMessage(pattern=r'\.afk (.*)', outgoing=True))
async def set_afk(event):
    global is_afk, afk_reason
    is_afk = True
    afk_reason = event.pattern_match.group(1)
    await event.respond(
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
        await event.respond("✅ **User has returned. AFK deactivated.**")


# 4. AFK AUTO-RESPONDER: Polite away message for DMs
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def afk_responder(event):
    global is_afk, afk_reason
    # Prevent the bot from replying to its own messages or commands
    if is_afk and not event.text.startswith('.'):
        await event.reply(
            f"🛡️ **Automated Defense System:**\n\n"
            f"The user is currently away from their keyboard.\n"
            f"📝 **Given Reason:** `{afk_reason}`\n\n"
            f"_Please leave your message and they will respond upon return._"
        )


# 5. PURGE (Delete your own messages fast)
@client.on(events.NewMessage(pattern=r'\.del', outgoing=True))
async def delete_msg(event):
    if event.is_reply:
        replied_msg = await event.get_reply_message()
        try:
            await replied_msg.delete()
            await event.delete()
        except:
            pass # Bots can only delete messages if they have admin rights


if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 VIZARD USERBOT INITIATING...")
    print("="*50 + "\n")
    # ✅ Start the client using the Bot Token
    client.start(bot_token=BOT_TOKEN)
    print("✅ CONNECTION ESTABLISHED! LISTENING ON TELEGRAM...")
    client.run_until_disconnected()
