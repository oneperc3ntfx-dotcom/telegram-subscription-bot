import os
import re
import time
import requests
import threading
from datetime import datetime, timezone

from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
APPS_SCRIPT_URL = os.getenv("APPS_SCRIPT_URL")

MONITOR_GROUP = -1004311537613
TARGET_GROUP = -1002510797113

REDIRECT_LINK = "https://t.me/AITOOLSIGNAL_BOT?start"

seen_users = set()

# ================= MESSAGE PARSER =================
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
        r = requests.post(APPS_SCRIPT_URL, json=data, timeout=30)
        print("📊 RESPONSE:", r.status_code, r.text)
    except Exception as e:
        print("❌ SHEET ERROR:", e)

# ================= FOLLOW UP MESSAGE =================
def follow_up_message():
    return (
        "🚨 AKSES ANDA SUDAH BERAKHIR / TIDAK VALID\n\n"
        "👉 Silakan lanjutkan akses di link berikut:\n"
        f"{REDIRECT_LINK}\n\n"
        "⚡ Sistem akan otomatis memproses setelah pembayaran."
    )

# ================= HANDLE GROUP (MONITOR ONLY) =================
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

    if data["userId"] in seen_users:
        return

    seen_users.add(data["userId"])

    print("━━━━━━━━━━━━━━")
    print("CHAT ID:", chat_id)
    print("JOIN DETECTED:", data)

    # SAVE TO SHEET
    send_to_sheet(data)

    # UNBAN FOR RENEW SYSTEM
    try:
        await context.bot.unban_chat_member(
            chat_id=TARGET_GROUP,
            user_id=int(data["userId"]),
            only_if_banned=True
        )
        print("♻️ UNBAN SUCCESS:", data["userId"])
    except Exception as e:
        print("UNBAN ERROR:", e)

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(follow_up_message())

# ================= CHAT RANDOM / DM =================
async def catch_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(follow_up_message())

# ================= EXPIRY CHECK =================
def is_expired(kick_date_str):
    try:
        if not kick_date_str:
            return False

        try:
            kd = datetime.fromisoformat(
                kick_date_str.replace("Z", "+00:00")
            )
        except:
            kd = datetime.strptime(kick_date_str, "%Y-%m-%d %H:%M")
            kd = kd.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)

        return now >= kd

    except Exception as e:
        print("PARSE ERROR:", e)
        return False

# ================= WORKER LOOP =================
def kick_worker_loop(app):
    while True:
        try:
            r = requests.get(APPS_SCRIPT_URL, timeout=30)
            data = r.json().get("data", [])

            print("━━━━━━━━━━━━━━")
            print("CHECKING SHEET DATA...")

            for u in data:
                user_id = u.get("userId")
                kick_date = u.get("kickDate")
                out = u.get("out")

                if not user_id:
                    continue

                if out == "✔":
                    continue

                print("CHECK:", user_id, kick_date)

                if is_expired(kick_date):

                    try:
                        print("🔥 AUTO KICK:", user_id)

                        app.bot.ban_chat_member(
                            chat_id=TARGET_GROUP,
                            user_id=int(user_id)
                        )

                        app.bot.send_message(
                            chat_id=int(user_id),
                            text=follow_up_message()
                        )

                        print("🔥 KICKED:", user_id)

                    except Exception as e:
                        print("❌ KICK ERROR:", e)

        except Exception as e:
            print("❌ LOOP ERROR:", e)

        time.sleep(60)

# ================= MAIN (FIXED ROUTING ORDER) =================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    print("BOT RUNNING")

    # ORDER WAJIB BENAR (INI YANG FIX BUG KAMU)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Chat(MONITOR_GROUP), handle_group))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, catch_all))

    threading.Thread(target=kick_worker_loop, args=(app,), daemon=True).start()

    app.run_polling()


if __name__ == "__main__":
    main()
