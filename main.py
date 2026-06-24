import os
import re
import threading
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
APPS_SCRIPT_URL = os.getenv("APPS_SCRIPT_URL")
GROUP_ID = os.getenv("GROUP_ID")

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
    requests.post(APPS_SCRIPT_URL, json=data)

# ================= GROUP MESSAGE HANDLER =================
async def handle_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "SUCCESS JOIN TO GROUP" not in text:
        return

    data = parse_message(text)
    send_to_sheet(data)

    print("SAVED:", data["userId"])

# ================= PRIVATE CHAT HANDLER (REDIRECT BOT) =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Klik untuk lanjut:\n{REDIRECT_LINK}"
    )

# ================= BOT START =================
def run():
    app = Application.builder().token(BOT_TOKEN).build()

    # grup monitor
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_group))

    # private chat redirect
    app.add_handler(CommandHandler("start", start))

    print("BOT RUNNING")
    app.run_polling()

if __name__ == "__main__":
    run()
