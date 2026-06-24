import os
import re
import time
import threading
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
    return {
        "username": re.search(r"Username:\s(@\w+)", text).group(1) if re.search(r"Username:", text) else "",
        "userId": re.search(r"User ID:\s(\d+)", text).group(1) if re.search(r"User ID:", text) else "",
        "paket": re.search(r"Paket:\s(\d+)", text).group(1) if re.search(r"Paket:", text) else "1",
        "referral": re.search(r"Referral:\s(.+)", text).group(1) if re.search(r"Referral:", text) else ""
    }

# ================= SEND TO SHEET (DEBUG FULL) =================
def send_to_sheet(data):
    try:
        print("📤 SENDING TO SHEET:", data)

        r = requests.post(APPS_SCRIPT_URL, json=data, timeout=10)

        print("📊 SHEET STATUS:", r.status_code)
        print("📊 SHEET RESPONSE:", r.text[:300])

    except Exception as e:
        print("❌ SHEET ERROR:", e)

# ================= GROUP HANDLER (DEBUG FULL) =================
async def handle_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        msg = update.message or update.channel_post

        if not msg:
            print("❌ NO MESSAGE OBJECT")
            return

        chat_id = msg.chat_id
        text = msg.text or ""

        print("━━━━━━━━━━━━━━━━━━━━━━")
        print("📩 CHAT ID:", chat_id)
        print("📩 TEXT:", text)

        if chat_id != MONITOR_GROUP:
            print("❌ WRONG GROUP - IGNORE")
            return

        if "SUCCESS JOIN TO GROUP" not in text:
            print("❌ NOT TARGET MESSAGE")
            return

        data = parse_message(text)

        print("✅ PARSED DATA:", data)

        send_to_sheet(data)

    except Exception as e:
        print("❌ HANDLER ERROR:", e)

# ================= START COMMAND =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Klik untuk lanjut:\n{REDIRECT_LINK}"
    )

# ================= KICK WORKER (DEBUG FULL) =================
def kick_worker():
    bot = Bot(token=BOT_TOKEN)

    while True:
        try:
            print("🔄 CHECKING EXPIRED DATA...")

            r = requests.get(APPS_SCRIPT_URL, timeout=10)

            print("📡 RAW RESPONSE:", r.text[:200])

            try:
                result = r.json()
                data = result.get("data", [])
            except Exception:
                print("❌ INVALID JSON FROM SHEET")
                data = []

            today = time.strftime("%Y-%m-%d")

            for row in data:
                print("CHECK ROW:", row)

                if row.get("kickDate") == today and row.get("out") != "✔":
                    try:
                        print("🚨 KICKING:", row["userId"])

                        bot.ban_chat_member(
                            chat_id=TARGET_GROUP,
                            user_id=int(row["userId"])
                        )

                        bot.send_message(
                            chat_id=row["userId"],
                            text=f"Langganan kamu sudah habis.\nUpgrade di sini:\n{REDIRECT_LINK}"
                        )

                    except Exception as e:
                        print("❌ KICK ERROR:", e)

        except Exception as e:
            print("❌ KICK WORKER ERROR:", e)

        time.sleep(60 * 60)

# ================= RUN =================
def run():
    app = Application.builder().token(BOT_TOKEN).build()

    # IMPORTANT: only group messages
    app.add_handler(MessageHandler(filters.TEXT, handle_group))
    app.add_handler(CommandHandler("start", start))

    print("🚀 BOT RUNNING")

    threading.Thread(target=kick_worker, daemon=True).start()

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    run()
