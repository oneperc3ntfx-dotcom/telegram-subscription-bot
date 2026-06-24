# Telegram Subscription Bot (Apps Script Version)

## Features
- Auto capture group messages
- Admin-only data processing
- Google Sheets storage
- Auto kick expired users
- Auto message after expiration
- Non-admin redirect system

## Setup

1. Deploy Apps Script as Web App
2. Set webhook:
https://api.telegram.org/bot<TOKEN>/setWebhook?url=<WEB_APP_URL>

3. Set triggers:
- checkKick → daily 00:00

## Sheet Structure
Username | UserID | Paket | Harga | Durasi | Kick Date | Referral | OUT
