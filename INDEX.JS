import express from "express";
import bodyParser from "body-parser";
import axios from "axios";
import { CONFIG } from "./config.js";

const app = express();
app.use(bodyParser.json());

// ======================
// WEBHOOK ENTRY
// ======================
app.post("/webhook", async (req, res) => {
  try {
    const msg = req.body.message;
    if (!msg) return res.sendStatus(200);

    const text = msg.text || "";
    const userId = msg.from.id;
    const chatId = msg.chat.id;

    // NON ADMIN
    if (!CONFIG.ADMINS.includes(userId)) {
      return replyNonAdmin(chatId);
    }

    // ADMIN
    processAdmin(text);

    res.sendStatus(200);

  } catch (err) {
    console.log(err);
    res.sendStatus(200);
  }
});

// ======================
// ADMIN PROCESS
// ======================
async function processAdmin(text) {

  const username = text.match(/Username:\s*(.*)/)?.[1] || "";
  const userId = text.match(/User ID:\s*(\d+)/)?.[1] || "";
  const paket = text.match(/Paket:\s*(.*)/)?.[1] || "";
  const harga = text.match(/Harga:\s*(.*)/)?.[1] || "";

  const durasi = (paket.match(/(\d+)\s*Bulan/) || [0,0])[1];

  const kickDate = new Date();
  kickDate.setMonth(kickDate.getMonth() + parseInt(durasi));

  console.log({
    username,
    userId,
    paket,
    harga,
    kickDate
  });

  // TODO: simpan ke Google Sheets API
}

// ======================
// NON ADMIN REPLY
// ======================
async function replyNonAdmin(chatId) {
  const url = `https://api.telegram.org/bot${CONFIG.TOKEN}/sendMessage`;

  await axios.post(url, {
    chat_id: chatId,
    text: `Silahkan hubungi ke sini:\n${CONFIG.BOT_LINK}`
  });
}

// ======================
// START SERVER
// ======================
app.listen(process.env.PORT || 3000, () => {
  console.log("Bot running...");
});
