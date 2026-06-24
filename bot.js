const { Telegraf } = require("telegraf");
require("dotenv").config();

const { sendToSheet } = require("./sheetApi");
const { checkKick } = require("./kickWorker");

const bot = new Telegraf(process.env.BOT_TOKEN);

// PARSER
function parseMessage(text) {
  const username = text.match(/Username:\s(@\w+)/)?.[1] || "";
  const userId = text.match(/User ID:\s(\d+)/)?.[1];
  const paketText = text.match(/Paket:\s(\d+)/)?.[1] || "1";
  const referral = text.match(/Referral:\s(.+)/)?.[1] || "";

  return {
    username,
    userId,
    paket: paketText,
    referral
  };
}

// DETECT JOIN MESSAGE
bot.on("text", async (ctx) => {
  const text = ctx.message.text;

  if (!text.includes("SUCCESS JOIN TO GROUP")) return;

  const data = parseMessage(text);

  await sendToSheet(data);

  console.log("Saved:", data.userId);
});

bot.launch();

// CEK KICK SETIAP 1 JAM
setInterval(() => {
  checkKick(bot);
}, 60 * 60 * 1000);

checkKick(bot);

console.log("Bot running...");
