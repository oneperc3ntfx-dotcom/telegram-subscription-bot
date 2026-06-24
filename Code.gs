function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const message = data.message;

    if (!message || !message.text) return;

    const text = message.text;
    const senderId = message.from.id;

    // NON ADMIN
    if (!CONFIG.ADMINS.includes(senderId)) {
      replyNonAdmin(message.chat.id);
      return;
    }

    // ADMIN
    processAdminMessage(text);

  } catch (err) {
    Logger.log("ERROR doPost: " + err);
  }
}
