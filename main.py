import os
import re
import time
import threading
import requests
from datetime import datetime
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
APPS_SCRIPT_URL = os.getenv("APPS_SCRIPT_URL")

MONITOR_GROUP = -1004311537613
TARGET_GROUP = -1002510797113

REDIRECT_LINK = "https://t.me/AITOOLSIGNAL_BOT?start"

seen_users = set()
bot = Bot(token=BOT_TOKEN)

# ================= PARSER =================
def parse_message(text):
    username = re.search(r"Username:\s*(.+)", text)
    user_id = re.search(r"User ID:\s*(\d+)", text)
    paket = re.search(r"Paket:\s*(.+)", text)
    harga = re.search(r"Harga:\s*Rp\s*([\d,.]+)", text)
    referral = re.search(r"Referral:\s*(.+)", text)

    return {
        "username": username.group(1).strip() if username else "",
        "userId": user_id.group(1).strip() if user_id else "",
        "paket": paket.group(1).strip() if paket else "",
        "harga": harga.group(1).strip() if harga else "",
        "referral": referral.group(1).strip() if referral else ""
    }

# ================= SEND TO SHEET =================
def send_to_sheet(data):
    try:
        print("📤 SEND:", data)
        r = requests.post(APPS_SCRIPT_URL, json=data, timeout=30)
        print("📊 RESPONSE:", r.status_code, r.text)
    except Exception as e:
        print("❌ SHEET ERROR:", e)

# ================= SAFE PARSE KICK DATE =================
def parse_kick_date(kick_date):
    try:
        if not kick_date:
            return None

        kick_date = str(kick_date).strip()

        # buang detik kalau ada
        if len(kick_date) > 16:
            kick_date = kick_date[:16]

        return datetime.strptime(kick_date, "%Y-%m-%d %H:%M")

    except Exception as e:
        print("❌ PARSE ERROR:", kick_date, e)
        return None

def is_expired(kick_date):
    dt = parse_kick_date(kick_date)
    if not dt:
        return False

    return datetime.now() >= dt

# ================= HANDLE GROUP =================
async def handle_group(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = (
        update.message
        or update.channel_post
        or update.edited_message
        or update.edited_channel_post
    )

    if not msg:
        return

    text = msg.text or msg.caption or ""
    chat_id = msg.chat.id
    user_id = msg.from_user.id if msg.from_user else None

    print("━━━━━━━━━━━━━━")
    print("CHAT ID:", chat_id)
    print("TEXT:\n", text)

    if chat_id != MONITOR_GROUP:
        return

    if "SUCCESS JOIN TO GROUP" not in text:
        return

    data = parse_message(text)

    if not data["userId"]:
        return

    if data["userId"] in seen_users:
        return

    seen_users.add(data["userId"])

    print("SAVED:", data["userId"])
    send_to_sheet(data)

# ================= START COMMAND =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🚀 Start Bot AI Toolsignal:\n{REDIRECT_LINK}"
    )

# ================= KICK WORKER =================
def kick_worker():
    bot = Bot(token=BOT_TOKEN)

    while True:
        try:
            r = requests.get(APPS_SCRIPT_URL, timeout=30)
            data = r.json().get("data", [])

            print("━━━━━━━━━━━━━━")
            print("CHECKING KICK DATA...")

            for u in data:
                user_id = u.get("userId")
                kick_date = u.get("kickDate")
                out = u.get("out")

                print("CHECK:", user_id, kick_date, out)

                if not user_id:
                    continue

                if out == "✔":
                    continue

                if is_expired(kick_date):
                    try:
                        bot.ban_chat_member(
                            chat_id=TARGET_GROUP,
                            user_id=int(user_id)
                        )

                        bot.send_message(
                            chat_id=user_id,
                            text=f"❌ Membership habis.\n👉 Start: {REDIRECT_LINK}"
                        )

                        requests.post(APPS_SCRIPT_URL, json={
                            "action": "markOut",
                            "userId": user_id
                        }, timeout=10)

                        print("🔥 KICKED:", user_id)

                    except Exception as e:
                        print("❌ KICK ERROR:", e)

        except Exception as e:
            print("❌ KICK LOOP ERROR:", e)

        time.sleep(60)

# ================= RUN =================
def run():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.ALL, handle_group))
    app.add_handler(CommandHandler("start", start))

    print("BOT RUNNING")

    threading.Thread(target=kick_worker, daemon=True).start()

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    run()
