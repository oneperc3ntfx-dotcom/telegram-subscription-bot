import time
import requests
from datetime import datetime, timezone

def is_expired(kick_date_str):
    try:
        if not kick_date_str:
            return False

        # FIX: support 2 format
        try:
            kick_date = datetime.fromisoformat(
                kick_date_str.replace("Z", "+00:00")
            )
        except:
            kick_date = datetime.strptime(
                kick_date_str,
                "%Y-%m-%d %H:%M"
            )

        now = datetime.now(timezone.utc)

        return now >= kick_date.replace(tzinfo=timezone.utc)

    except Exception as e:
        print("PARSE ERROR:", e)
        return False


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

                print("CHECK:", user_id, kick_date)

                if not user_id:
                    continue

                if out == "✔":
                    continue

                if is_expired(kick_date):

                    try:
                        print("🔥 KICKING:", user_id)

                        res = app.bot.ban_chat_member(
                            chat_id=TARGET_GROUP,
                            user_id=int(user_id)
                        )

                        print("TELEGRAM RESULT:", res)

                        app.bot.send_message(
                            chat_id=int(user_id),
                            text=f"❌ Membership kamu habis.\n👉 Start lagi: {REDIRECT_LINK}"
                        )

                        print("🔥 KICKED:", user_id)

                    except Exception as e:
                        print("❌ KICK ERROR:", e)

        except Exception as e:
            print("❌ LOOP ERROR:", e)

        time.sleep(60)
