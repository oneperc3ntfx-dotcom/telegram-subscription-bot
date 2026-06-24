import time
import requests
from telegram import Bot

# ================= CONFIG =================
BOT_TOKEN = "ISI_DI_ENV"  # atau os.getenv kalau digabung
APPS_SCRIPT_URL = "ISI_DI_ENV"

TARGET_GROUP = -1002510797113
REDIRECT_LINK = "https://t.me/AITOOLSIGNAL_BOT?start"

# ================= INIT BOT =================
bot = Bot(token=BOT_TOKEN)

# ================= GET DATA =================
def fetch_data():
    try:
        r = requests.get(APPS_SCRIPT_URL, timeout=10)

        print("📡 RAW RESPONSE:", r.text[:300])

        data = r.json()
        return data.get("data", [])

    except Exception as e:
        print("❌ FETCH ERROR:", e)
        return []

# ================= KICK MEMBER =================
def kick_member(user_id):
    try:
        print("🚨 KICKING USER:", user_id)

        bot.ban_chat_member(
            chat_id=TARGET_GROUP,
            user_id=int(user_id)
        )

        bot.send_message(
            chat_id=user_id,
            text=(
                "⚠️ Langganan kamu sudah habis.\n\n"
                "Silakan upgrade kembali di:\n"
                f"{REDIRECT_LINK}"
            )
        )

        print("✅ KICK SUCCESS:", user_id)

    except Exception as e:
        print("❌ KICK ERROR:", e)

# ================= WORKER LOOP =================
def kick_worker():
    while True:
        try:
            print("🔄 CHECKING EXPIRED USERS...")

            users = fetch_data()

            today = time.strftime("%Y-%m-%d")

            for u in users:
                print("CHECK:", u)

                if u.get("kickDate") == today and u.get("out") != "✔":
                    kick_member(u["userId"])

        except Exception as e:
            print("❌ WORKER ERROR:", e)

        time.sleep(3600)  # 1 jam sekali

# ================= RUN =================
if __name__ == "__main__":
    print("🚀 KICK WORKER RUNNING")
    kick_worker()
