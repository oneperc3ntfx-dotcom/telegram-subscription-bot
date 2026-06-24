// =======================
// ADMIN PROCESS
// =======================
function processAdminMessage(text) {

  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEET_NAME);

  const username = text.match(/Username:\s*(.*)/)?.[1] || "";
  const userId = text.match(/User ID:\s*(\d+)/)?.[1] || "";
  const paket = text.match(/Paket:\s*(.*)/)?.[1] || "";
  const harga = text.match(/Harga:\s*(.*)/)?.[1] || "";
  const referral = text.match(/Referral:\s*(.*)/)?.[1] || "";

  const durasiMatch = paket.match(/(\d+)\s*Bulan/);
  const durasi = durasiMatch ? parseInt(durasiMatch[1]) : 0;

  const kickDate = new Date();
  kickDate.setMonth(kickDate.getMonth() + durasi);

  sheet.appendRow([
    username,
    userId,
    paket,
    harga,
    durasi,
    kickDate,
    referral,
    ""
  ]);
}


// =======================
// NON ADMIN REPLY
// =======================
function replyNonAdmin(chatId) {

  const url = `https://api.telegram.org/bot${CONFIG.TOKEN}/sendMessage`;

  const text =
`Silahkan hubungi ke sini untuk informasi Signal AI:

👉 ${CONFIG.BOT_LINK}`;

  UrlFetchApp.fetch(url, {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify({
      chat_id: chatId,
      text: text,
      disable_web_page_preview: true
    })
  });
}


// =======================
// CHECK EXPIRED + KICK
// =======================
function checkKick() {

  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEET_NAME);
  const data = sheet.getDataRange().getValues();

  const today = new Date();
  today.setHours(0,0,0,0);

  for (let i = 1; i < data.length; i++) {

    const userId = data[i][1];
    const kickDate = new Date(data[i][5]);
    const out = data[i][7];

    kickDate.setHours(0,0,0,0);

    if (kickDate.getTime() === today.getTime() && out !== "✔") {

      kickUser(userId);
      sendMessage(userId);

      sheet.getRange(i+1, 8).setValue("✔");
    }
  }
}


// =======================
// KICK USER
// =======================
function kickUser(userId) {

  const url = `https://api.telegram.org/bot${CONFIG.TOKEN}/banChatMember`;

  const payload = {
    chat_id: CONFIG.GROUP_ID,
    user_id: userId
  };

  UrlFetchApp.fetch(url, {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify(payload)
  });
}


// =======================
// SEND MESSAGE AFTER KICK
// =======================
function sendMessage(userId) {

  const url = `https://api.telegram.org/bot${CONFIG.TOKEN}/sendMessage`;

  const text =
`Langganan Kamu Telah Selesai...

Silahkan Upgrade:
👉 ${CONFIG.UPGRADE_LINK}`;

  UrlFetchApp.fetch(url, {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify({
      chat_id: userId,
      text: text
    })
  });
}
