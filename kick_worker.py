import asyncio
import requests

async def kick_worker_async(app):

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

                if is_expired(kick_date):

                    try:
                        print("🔥 KICK:", user_id)

                        # ✔ PAKAI app.bot (INI WAJIB)
                        await app.bot.ban_chat_member(
                            chat_id=TARGET_GROUP,
                            user_id=int(user_id)
                        )

                        await app.bot.send_message(
                            chat_id=int(user_id),
                            text=f"❌ Membership habis.\n👉 Start lagi: {REDIRECT_LINK}"
                        )

                        print("🔥 KICKED:", user_id)

                    except Exception as e:
                        print("❌ KICK ERROR:", e)

        except Exception as e:
            print("❌ LOOP ERROR:", e)

        await asyncio.sleep(60)
