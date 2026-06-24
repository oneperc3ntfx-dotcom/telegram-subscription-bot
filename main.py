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

seen_users = set()

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
        "paket": paket.group(1).strip() if paket else "1",
        "harga": harga.group(1).strip() if harga else "",
        "referral": referral.group(1).strip() if referral else ""
    }

# ================= SEND TO SHEET =================
def send_to_sheet(data):
    try:
        print("📤 SEND TO SHEET:", data)

        r = requests.post(
            APPS_SCRIPT_URL,
            json=data,
            timeout=30
        )

        print("📊 RESPONSE:", r.status_code, r.text)

    except Exception as e:
        print("❌ SHEET ERROR:", e)

# ================= HANDLE GROUP =================
async def handle_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("🔔 UPDATE RECEIVED")

    msg = update.message or update.effective_message
    if not msg:
        return

    chat_id = msg.chat_id
    text = msg.text or msg.caption or ""

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
        f"Klik untuk lanjut:\n{REDIRECT_LINK}"
    )

# ================= KICK WORKER =================
def kick_worker():
    bot = Bot(token=BOT_TOKEN)

    while True:
        try:
            r = requests.get(APPS_SCRIPT_URL, timeout=30)
            data = r.json().get("data", [])

            today = time.strftime("%Y-%m-%d")

            for u in data:
                if u.get("kickDate") == today and u.get("out") != "✔":
                    try:
                        bot.ban_chat_member(
                            chat_id=TARGET_GROUP,
                            user_id=int(u["userId"])
                        )

                        bot.send_message(
                            chat_id=u["userId"],
                            text=f"Langganan kamu sudah habis.\nStart lagi: {REDIRECT_LINK}"
                        )

                        print("KICKED:", u["userId"])

                    except Exception as e:
                        print("KICK ERROR:", e)

        except Exception as e:
            print("KICK LOOP ERROR:", e)

        time.sleep(3600)

# ================= RUN =================
def run():
    app = Application.builder().token(BOT_TOKEN).build()

    # 🔥 IMPORTANT: capture ALL group messages
    app.add_handler(MessageHandler(filters.ChatType.GROUPS, handle_group))

    app.add_handler(CommandHandler("start", start))

    print("BOT RUNNING")

    threading.Thread(target=kick_worker, daemon=True).start()

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    run()
