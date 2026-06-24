import os
import re
import time
import threading
import json
import requests
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
APPS_SCRIPT_URL = os.getenv("APPS_SCRIPT_URL")

MONITOR_GROUP = -1004415837135
TARGET_GROUP = -1002510797113

REDIRECT_LINK = "https://t.me/AITOOLSIGNAL_BOT?start"

# ================= PARSER =================
def parse_message(text):
    username = re.search(r"Username:\s*(.+)", text)
    user_id = re.search(r"User ID:\s*(\d+)", text)
    paket = re.search(r"Paket:\s*(.+)", text)
    referral = re.search(r"Referral:\s*(.+)", text)

    return {
        "username": username.group(1).strip() if username else "",
        "userId": user_id.group(1).strip() if user_id else "",
        "paket": paket.group(1).strip() if paket else "1",
        "referral": referral.group(1).strip() if referral else ""
    }

# ================= SEND TO SHEET =================
def send_to_sheet(data):
    try:
        print("📤 SEND TO SHEET:", data)

        r = requests.post(
            APPS_SCRIPT_URL,
            json=data,
            timeout=10
        )

        print("📊 STATUS:", r.status_code)
        print("📊 RESPONSE:", r.text)

    except Exception as e:
        print("❌ SHEET ERROR:", e)

# ================= HANDLER =================
async def handle_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        msg = update.effective_message
        if not msg:
            return

        chat_id = update.effective_chat.id
        text = msg.text or ""

        print("━━━━━━━━━━━━━━━━")
        print("CHAT ID:", chat_id)
        print("TEXT:\n", text)

        if chat_id != MONITOR_GROUP:
            return

        if "SUCCESS JOIN TO GROUP" not in text:
            return

        data = parse_message(text)

        print("SAVED:", data["userId"])

        send_to_sheet(data)

    except Exception as e:
        print("ERROR:", e)

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Klik untuk lanjut:\n{REDIRECT_LINK}"
    )

# ================= KICK WORKER =================
def kick_worker():
    bot = Bot(token=BOT_TOKEN)

    while True:
        try:
            r = requests.get(APPS_SCRIPT_URL, timeout=10)

            try:
                result = r.json()
                data = result.get("data", [])
            except:
                print("❌ INVALID JSON")
                data = []

            today = time.strftime("%Y-%m-%d")

            for row in data:
                if row.get("kickDate") == today and row.get("out") != "✔":
                    try:
                        bot.ban_chat_member(
                            chat_id=TARGET_GROUP,
                            user_id=int(row["userId"])
                        )

                        bot.send_message(
                            chat_id=row["userId"],
                            text=f"Langganan kamu sudah habis.\nStart ulang: {REDIRECT_LINK}"
                        )

                        print("KICKED:", row["userId"])

                    except Exception as e:
                        print("KICK ERROR:", e)

        except Exception as e:
            print("KICK LOOP ERROR:", e)

        time.sleep(3600)

# ================= RUN =================
def run():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT, handle_group))
    app.add_handler(CommandHandler("start", start))

    print("BOT RUNNING")

    threading.Thread(target=kick_worker, daemon=True).start()

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    run()
