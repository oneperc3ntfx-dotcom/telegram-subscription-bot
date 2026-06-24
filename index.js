import express from "express";
import axios from "axios";
import bodyParser from "body-parser";
import { CONFIG } from "./config.js";

const app = express();
app.use(bodyParser.json());

// =====================
// WEBHOOK TELEGRAM
// =====================
app.post("/webhook", async (req, res) => {
  try {

    const msg = req.body.message;
    if (!msg || !msg.text) return res.sendStatus(200);

    const text = msg.text;
    const userId = msg.from.id;
    const chatId = msg.chat.id;

    // NON ADMIN
    if (!CONFIG.ADMINS.includes(userId)) {
      await axios.post(`https://api.telegram.org/bot${CONFIG.BOT_TOKEN}/sendMessage`, {
        chat_id: chatId,
        text: `Silahkan hubungi:\n${CONFIG.BOT_LINK}`
      });

      return res.sendStatus(200);
    }

    // ADMIN → PARSE DATA
    const username = text.match(/Username:\s*(.*)/)?.[1] || "";
    const userIdText = text.match(/User ID:\s*(\d+)/)?.[1] || "";
    const paket = text.match(/Paket:\s*(.*)/)?.[1] || "";
    const harga = text.match(/Harga:\s*(.*)/)?.[1] || "";
    const referral = text.match(/Referral:\s*(.*)/)?.[1] || "";

    // SEND TO APPS SCRIPT
    await axios.post(CONFIG.APPS_SCRIPT_URL, {
      username,
      userId: userIdText,
      paket,
      harga,
      referral
    });

    console.log("DATA SENT TO SHEET");

    res.sendStatus(200);

  } catch (err) {
    console.log(err);
    res.sendStatus(200);
  }
});

app.listen(process.env.PORT || 3000, () => {
  console.log("BOT RUNNING");
});
