import os
import re
import time
import threading
import requests
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    filters,
    ContextTypes
)

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
APPS_SCRIPT_URL = os.getenv("APPS_SCRIPT_URL")

MONITOR_GROUP = -1004415837135
TARGET_GROUP = -1002510797113

REDIRECT_LINK = "https://t.me/AITOOLSIGNAL_BOT?start"

# ================= PARSER =================
def parse_message(text):
    return {
        "username": re.search(r"Username:\s(@\w+)", text).group(1) if re.search(r"Username:", text) else "",
        "userId": re.search(r"User ID:\s(\d+)", text).group(1) if re.search(r"User ID:", text) else "",
        "paket": re.search(r"Paket:\s(\d+)", text).group(1) if re.search(r"Paket:", text) else "1",
        "referral": re.search(r"Referral:\s(.+)", text).group(1) if re.search(r"Referral:", text) else ""
    }

# ================= SEND TO SHEET =================
def send_to_sheet(data):
    try:
        requests.post(APPS_SCRIPT_URL, json=data, timeout=10)
    except Exception as e:
        print("SHEET ERROR:", e)

# ================= GROUP HANDLER =================
async def handle_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.message.chat_id
        text = update.message.text or ""

        # hanya group monitor
        if chat_id != MONITOR_GROUP:
            return

        if "SUCCESS JOIN TO GROUP" not in text:
            return

        data = parse_message(text)
        send_to_sheet(data)

        print("SAVED:", data["userId"])

    except Exception as e:
        print("HANDLE ERROR:", e)

# ================= START COMMAND (REDIRECT BOT) =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Klik untuk lanjut:\n{REDIRECT_LINK}"
    )

# ================= KICK WORKER =================
def kick_worker():
    from telegram import Bot
    bot = Bot(token=BOT_TOKEN)

    while True:
        try:
            r = requests.get(APPS_SCRIPT_URL + "?action=get", timeout=10)
            data = r.json()

            today = time.strftime("%Y-%m-%d")

            for row in data:
                if row.get("kickDate") == today and row.get("out") != "✔":
                    user_id = row.get("userId")

                    try:
                        # kick user dari TARGET GROUP
                        bot.ban_chat_member(
                            chat_id=TARGET_GROUP,
                            user_id=user_id
                        )

                        bot.send_message(
                            chat_id=user_id,
                            text=f"Langganan Kamu Telah Selesai.\nSilahkan Upgrade:\n{REDIRECT_LINK}"
                        )

                        print("KICKED:", user_id)

                    except Exception as e:
                        print("KICK ERROR:", e)

        except Exception as e:
            print("KICK WORKER ERROR:", e)

        time.sleep(3600)  # tiap 1 jam

# ================= RUN BOT =================
def run():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_group))
    app.add_handler(CommandHandler("start", start))

    print("BOT RUNNING")

    # start kick thread
    threading.Thread(target=kick_worker, daemon=True).start()

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    run()
