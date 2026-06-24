import os
import re
import time
import requests
import threading
from datetime import datetime, timezone

from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
APPS_SCRIPT_URL = os.getenv("APPS_SCRIPT_URL")

MONITOR_GROUP = -1004311537613
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

# ================= HANDLE GROUP =================
async def handle_group(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = update.message or update.channel_post or update.edited_message
    if not msg:
        return

    text = msg.text or msg.caption or ""
    chat_id = msg.chat.id

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

    send_to_sheet(data)

    try:
        print("🔥 INSTANT KICK CHECK:", data["userId"])

        await context.bot.ban_chat_member(
            chat_id=TARGET_GROUP,
            user_id=int(data["userId"])
        )

        await context.bot.send_message(
            chat_id=int(data["userId"]),
            text=f"❌ Kamu sudah dikeluarkan dari grup.\n👉 Start lagi: {REDIRECT_LINK}"
        )

        print("🔥 INSTANT KICKED:", data["userId"])

    except Exception as e:
        print("❌ KICK ERROR:", e)

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🚀 Bot Active\n{REDIRECT_LINK}"
    )

# ================= WORKER LOOP =================
def kick_worker_loop():
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

                print("CHECK:", user_id, kick_date)

                if not user_id:
                    continue

                if out == "✔":
                    continue

                try:
                    if kick_date:

                        kd = None

                        # ================= DATE PARSER FIX =================
                        try:
                            # ISO format dari Google Sheets
                            kd = datetime.fromisoformat(
                                kick_date.replace("Z", "+00:00")
                            )
                        except:
                            # format lama fallback
                            kd = datetime.strptime(
                                kick_date,
                                "%Y-%m-%d %H:%M"
                            )

                        now = datetime.now(timezone.utc)

                        print("NOW:", now)
                        print("KICK:", kd)
                        print("EXPIRED:", now >= kd)

                        if now >= kd:

                            print("🔥 AUTO KICK:", user_id)

                            res = requests.post(
                                f"https://api.telegram.org/bot{BOT_TOKEN}/banChatMember",
                                json={
                                    "chat_id": TARGET_GROUP,
                                    "user_id": int(user_id)
                                },
                                timeout=30
                            )

                            print("TELEGRAM STATUS:", res.status_code)
                            print("TELEGRAM RESPONSE:", res.text)

                except Exception as e:
                    print("❌ DATE PARSE ERROR:", e)

        except Exception as e:
            print("❌ LOOP ERROR:", e)

        time.sleep(60)

# ================= MAIN =================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.ALL, handle_group))
    app.add_handler(CommandHandler("start", start))

    print("BOT RUNNING")

    threading.Thread(target=kick_worker_loop, daemon=True).start()

    app.run_polling()


if __name__ == "__main__":
    main()
