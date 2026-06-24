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

# 🔥 LINK BOT AI TOOL SIGNAL (START)
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
        print("📤 SEND TO SHEET:", data)

        r = requests.post(APPS_SCRIPT_URL, json=data, timeout=30)

        print("📊 RESPONSE:", r.status_code, r.text)

    except Exception as e:
        print("❌ SHEET ERROR:", e)

# ================= ADMIN CHECK =================
async def is_admin(update: Update, user_id: int):
    try:
        member = await update.effective_chat.get_member(user_id)
        return member.status in ["administrator", "creator"]
    except:
        return False

# ================= HANDLE GROUP / CHANNEL =================
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

    # hanya monitor group ini
    if chat_id != MONITOR_GROUP:
        return

    # ================= ADMIN CHECK =================
    if user_id:
        admin = await is_admin(update, user_id)

        if not admin:
            # 🚀 redirect ke bot AI toolsignal
            await update.effective_chat.send_message(
                f"⚠️ Kamu bukan admin.\n\n👉 Klik untuk lanjut:\n{REDIRECT_LINK}"
            )
            return

    # ================= FILTER MESSAGE =================
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
        f"🚀 Welcome!\nKlik untuk lanjut:\n{REDIRECT_LINK}"
    )

# ================= KICK SYSTEM =================
def is_expired(kick_date):
    if not kick_date:
        return False

    try:
        now = datetime.now()
        dt = datetime.strptime(kick_date, "%Y-%m-%d %H:%M")
        return now >= dt
    except:
        return False


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
                            text=f"❌ Membership kamu habis.\n👉 Start ulang: {REDIRECT_LINK}"
                        )

                        requests.post(APPS_SCRIPT_URL, json={
                            "action": "markOut",
                            "userId": user_id
                        }, timeout=10)

                        print("KICKED:", user_id)

                    except Exception as e:
                        print("KICK ERROR:", e)

        except Exception as e:
            print("KICK LOOP ERROR:", e)

        time.sleep(60)

# ================= RUN =================
def run():
    app = Application.builder().token(BOT_TOKEN).build()

    # monitor semua update (group + channel + bot message)
    app.add_handler(MessageHandler(filters.ALL, handle_group))

    app.add_handler(CommandHandler("start", start))

    print("BOT RUNNING")

    threading.Thread(target=kick_worker, daemon=True).start()

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    run()
