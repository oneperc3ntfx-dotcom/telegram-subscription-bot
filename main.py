import os
import re
import time
import requests
import threading
from datetime import datetime

from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
APPS_SCRIPT_URL = os.getenv("APPS_SCRIPT_URL")

MONITOR_GROUP = -1004311537613

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

# ================= SHEET =================
def send_to_sheet(data):
    try:
        print("📤 SEND TO SHEET:", data)
        requests.post(APPS_SCRIPT_URL, json=data, timeout=30)
    except Exception as e:
        print("❌ SHEET ERROR:", e)

# ================= HANDLE MONITOR GROUP =================
async def handle_group(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = update.message or update.channel_post or update.edited_message
    if not msg:
        return

    text = msg.text or msg.caption or ""
    chat_id = msg.chat.id

    if chat_id != MONITOR_GROUP:
        return

    if "SUCCESS JOIN TO GROUP" not in text:
        return

    data = parse_message(text)

    if not data["userId"]:
        return

    print("━━━━━━━━━━━━━━")
    print("JOIN DETECTED:", data)

    # kirim ke sheet
    send_to_sheet(data)

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Active")

# ================= PARSE KICK DATE =================
def parse_kick_date(value):
    try:
        if not value:
            return None
        return datetime.strptime(value, "%Y-%m-%d %H:%M")
    except:
        return None

# ================= WORKER CHECK SHEET =================
def sheet_worker():
    while True:
        try:
            r = requests.get(APPS_SCRIPT_URL, timeout=30)
            rows = r.json().get("data", [])

            now = datetime.now()

            print("━━━━━━━━━━━━━━")
            print("CHECKING SHEET...")

            for i, row in enumerate(rows):

                user_id = row.get("userId")
                kick_date = parse_kick_date(row.get("kickDate"))

                if not user_id or not kick_date:
                    continue

                print("CHECK:", user_id, kick_date)

                # kalau sudah lewat waktu
                if now >= kick_date:

                    print("🔥 EXPIRED:", user_id)

                    # tunggu 2 menit sebelum update sheet
                    time.sleep(120)

                    try:
                        # update Google Sheet via Apps Script (WAJIB endpoint update)
                        requests.post(APPS_SCRIPT_URL, json={
                            "action": "expire_update",
                            "userId": user_id
                        }, timeout=30)

                        print("✔ UPDATED SHEET:", user_id)

                    except Exception as e:
                        print("❌ UPDATE ERROR:", e)

        except Exception as e:
            print("❌ WORKER ERROR:", e)

        time.sleep(60)

# ================= MAIN =================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    print("BOT RUNNING")

    app.add_handler(MessageHandler(filters.Chat(MONITOR_GROUP), handle_group))
    app.add_handler(CommandHandler("start", start))

    threading.Thread(target=sheet_worker, daemon=True).start()

    app.run_polling()


if __name__ == "__main__":
    main()
