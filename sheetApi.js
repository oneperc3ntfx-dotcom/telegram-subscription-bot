const APPS_SCRIPT_URL = process.env.APPS_SCRIPT_URL;

async function sendToSheet(data) {
  await fetch(APPS_SCRIPT_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(data)
  });
}

module.exports = { sendToSheet };
