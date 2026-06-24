import asyncio
import requests
from telegram import Bot
from datetime import datetime, timezone

async def kick_worker_async():
    bot = Bot(token=BOT_TOKEN)

    while True:
        try:
            r = requests.get(APPS_SCRIPT_URL, timeout=30)
            data = r.json().get("data", [])

            print("━━━━━━━━━━━━━━")
            print("CHECKING KICK DATA...")

            for u in data:
                user_id = u.get("userId")
                kick_date = u.get("kickDate")
                out = u.get("out")

                print("CHECK:", user_id, kick_date, out)

                if not user_id:
                    continue

                if out == "✔":
                    continue

                # ================= DEBUG =================
                print("TARGET GROUP:", TARGET_GROUP)

                # ================= CHECK EXPIRED =================
                if is_expired(kick_date):

                    try:
                        print("🔥 TRY KICK:", user_id)

                        await bot.ban_chat_member(
                            chat_id=TARGET_GROUP,
                            user_id=int(user_id)
                        )

                        await bot.send_message(
                            chat_id=int(user_id),
                            text=f"❌ Membership kamu sudah habis.\n👉 Start lagi: {REDIRECT_LINK}"
                        )

                        # mark out ke sheet
                        requests.post(APPS_SCRIPT_URL, json={
                            "action": "markOut",
                            "userId": user_id
                        }, timeout=10)

                        print("🔥 KICKED SUCCESS:", user_id)

                    except Exception as e:
                        print("❌ KICK ERROR:", e)

        except Exception as e:
            print("❌ KICK LOOP ERROR:", e)

        await asyncio.sleep(60)
