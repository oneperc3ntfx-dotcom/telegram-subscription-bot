import { google } from "googleapis";

export async function appendSheet(auth, row, SHEET_ID) {
  const sheets = google.sheets({ version: "v4", auth });

  await sheets.spreadsheets.values.append({
    spreadsheetId: SHEET_ID,
    range: "DATA!A:H",
    valueInputOption: "RAW",
    requestBody: {
      values: [row]
    }
  });
}
