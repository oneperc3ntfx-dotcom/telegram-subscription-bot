import express from "express";
import axios from "axios";
import bodyParser from "body-parser";
import { CONFIG } from "./config.js";

const app = express();
app.use(bodyParser.json());


// ======================
// WEBHOOK TELEGRAM
// ======================
app.post("/webhook", async (req, res) => {
  try {

    const msg = req.body.message;
    if (!msg || !msg.text) return res.sendStatus(200);

    const text = msg.text;
    const userId = msg.from.id;
    const chatId = msg.chat.id;

    // NON ADMIN
    if (!CONFIG.ADMINS.includes(userId)) {
      await replyNonAdmin(chatId);
      return res.sendStatus(200);
    }

    // ADMIN PROCESS
    await processMessage(text);

    res.sendStatus(200);

  } catch (err) {
    console.log(err);
    res.sendStatus(200);
  }
});


// ======================
// PARSE & SEND TO APPS SCRIPT
// ======================
async function processMessage(text) {

  const username = text.match(/Username:\s*(.*)/)?.[1] || "";
  const userId = text.match(/User ID:\s*(\d+)/)?.[1] || "";
  const paket = text.match(/Paket:\s*(.*)/)?.[1] || "";
  const harga = text.match(/Harga:\s*(.*)/)?.[1] || "";
  const referral = text.match(/Referral:\s*(.*)/)?.[1] || "";

  try {

    await axios.post(CONFIG.APPS_SCRIPT_URL, {
      username,
      userId,
      paket,
      harga,
      referral
    });

    console.log("DATA SENT TO SHEET");

  } catch (err) {
    console.log("ERROR SEND:", err.message);
  }
}


// ======================
// NON ADMIN REPLY
// ======================
async function replyNonAdmin(chatId) {

  const url = `https://api.telegram.org/bot${CONFIG.BOT_TOKEN}/sendMessage`;

  await axios.post(url, {
    chat_id: chatId,
    text: `Silahkan hubungi bot ini untuk informasi Signal AI:\nhttps://t.me/AITOOLSIGNAL_BOT?start=signal`
  });
}


// ======================
// START SERVER
// ======================
app.listen(process.env.PORT || 3000, () => {
  console.log("Bot running on Railway");
});
