const dayjs = require("dayjs");

const APPS_SCRIPT_URL = process.env.APPS_SCRIPT_URL;
const GROUP_ID = process.env.GROUP_ID;

async function getData() {
  const res = await fetch(APPS_SCRIPT_URL + "?action=get");
  return await res.json();
}

async function checkKick(bot) {
  try {
    const data = await getData();
    const today = dayjs().format("YYYY-MM-DD");

    for (let row of data) {
      if (row.kickDate === today && row.out !== "✔") {
        try {
          await bot.telegram.banChatMember(GROUP_ID, row.userId);

          await bot.telegram.sendMessage(
            row.userId,
`Langganan Kamu Telah Selesai ...
Silahkan Upgrade Langganan kamu Dengan Disini https://t.me/AITOOLSIGNAL_BOT?start`
          );

          console.log("KICK:", row.userId);
        } catch (e) {
          console.log("ERR:", e.message);
        }
      }
    }
  } catch (err) {
    console.log(err.message);
  }
}

module.exports = { checkKick };
