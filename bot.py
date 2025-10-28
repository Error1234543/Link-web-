# bot.py
# Secure Invite Bot (auto-expiring invite links)
# Usage:
#   export BOT_TOKEN="your_bot_token_here"
#   export CHANNEL_ID="-1001234567890"
#   python bot.py

import os
import time
import threading
import requests
import telebot
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "-1003295571464")
EXPIRE_SECONDS = int(os.getenv("EXPIRE_SECONDS", "20"))
MEMBER_LIMIT = int(os.getenv("MEMBER_LIMIT", "1"))

if not BOT_TOKEN:
    raise SystemExit("Error: BOT_TOKEN environment variable not set. Set it before running the bot.")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

def create_invite_link():
    expire_date = int(time.time()) + EXPIRE_SECONDS
    payload = {"chat_id": CHANNEL_ID, "expire_date": expire_date, "member_limit": MEMBER_LIMIT}
    r = requests.post(f"{TG_API}/createChatInviteLink", json=payload, timeout=10)
    j = r.json()
    if not j.get("ok"):
        logging.error("createChatInviteLink failed: %s", j)
        raise Exception("Failed to create invite link")
    return j["result"]["invite_link"]

def revoke_link(link):
    payload = {"chat_id": CHANNEL_ID, "invite_link": link}
    try:
        requests.post(f"{TG_API}/revokeChatInviteLink", json=payload, timeout=10)
    except Exception as e:
        logging.exception("Failed to revoke link: %s", e)

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    try:
        link = create_invite_link()
    except Exception as e:
        logging.exception("Error creating invite link")
        bot.send_message(chat_id, "⚠️ Sorry, couldn't create an invite right now. Try again later.")
        return

    bot.send_message(chat_id, f"🔐 Here is your private channel link (valid for ~{EXPIRE_SECONDS} seconds):\n\n{link}\n\nNote: This link will expire shortly.")

    def revoke_and_notify(inv):
        time.sleep(EXPIRE_SECONDS)
        revoke_link(inv)
        try:
            bot.send_message(chat_id, "⏳ The invite has now expired. Send /start to request a new one.")
        except Exception:
            pass

    threading.Thread(target=lambda: revoke_and_notify(link), daemon=True).start()

if __name__ == '__main__':
    logging.info("Starting bot (long polling)...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)