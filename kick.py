import os
import time
import requests
from datetime import datetime
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
APPS_SCRIPT_URL = os.getenv("APPS_SCRIPT_URL")
GROUP_ID = os.getenv("GROUP_ID")

bot = Bot(token=BOT_TOKEN)

def get_data():
    r = requests.get(APPS_SCRIPT_URL + "?action=get")
    return r.json()

def run_kick_loop():
    while True:
        try:
            data = get_data()
            today = datetime.now().strftime("%Y-%m-%d")

            for row in data:
                if row["kickDate"] == today and row["out"] != "✔":
                    try:
                        bot.ban_chat_member(GROUP_ID, row["userId"])

                        bot.send_message(
                            row["userId"],
                            f"Langganan Kamu Telah Habis.\nSilahkan lanjut di:\n{REDIRECT_LINK}"
                        )

                        print("KICK:", row["userId"])

                    except Exception as e:
                        print("KICK ERROR:", e)

        except Exception as e:
            print("ERROR:", e)

        time.sleep(3600)  # tiap 1 jam
