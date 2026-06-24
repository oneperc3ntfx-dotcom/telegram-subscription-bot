const { Telegraf } = require("telegraf");

const { sendToSheet } = require("./sheetApi");
const { checkKick } = require("./kickWorker");

// ========================
// INIT BOT
// ========================
const bot = new Telegraf(process.env.BOT_TOKEN);

// ========================
// PARSER MESSAGE
// ========================
function parseMessage(text) {
  const username = text.match(/Username:\s(@\w+)/)?.[1] || "";
  const userId = text.match(/User ID:\s(\d+)/)?.[1] || "";
  const paketText = text.match(/Paket:\s(\d+)/)?.[1] || "1";
  const referral = text.match(/Referral:\s(.+)/)?.[1] || "";

  return {
    username,
    userId,
    paket: paketText,
    referral
  };
}

// ========================
// DETECT GROUP MESSAGE
// ========================
bot.on("text", async (ctx) => {
  try {
    const text = ctx.message.text;

    // hanya proses pesan tertentu
    if (!text.includes("SUCCESS JOIN TO GROUP")) return;

    const data = parseMessage(text);

    await sendToSheet(data);

    console.log("✅ SAVED:", data.userId);
  } catch (err) {
    console.log("❌ ERROR MESSAGE:", err.message);
  }
});

// ========================
// START BOT
// ========================
bot.launch();
console.log("🚀 Bot running...");

// ========================
// AUTO CHECK KICK (SETIAP 1 JAM)
// ========================
setInterval(async () => {
  try {
    await checkKick(bot);
  } catch (err) {
    console.log("❌ KICK ERROR:", err.message);
  }
}, 60 * 60 * 1000);

// RUN FIRST TIME SAAT START
checkKick(bot);
