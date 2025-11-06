# bot.py
# Secure Invite Bot with multiple channel support

import os
import time
import threading
import requests
import telebot
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

BOT_TOKEN = os.getenv("BOT_TOKEN")
EXPIRE_SECONDS = int(os.getenv("EXPIRE_SECONDS", "30"))  # 30 sec default
MEMBER_LIMIT = int(os.getenv("MEMBER_LIMIT", "1"))

if not BOT_TOKEN:
    raise SystemExit("Error: BOT_TOKEN environment variable not set.")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ------------------ CHANNEL MAP -------------------
# command_name : channel_id
CHANNEL_MAP = {
    "xd": "-1002511599219",       # replace with your /XD channel ID
    "alun": "-1003032615437",     # replace with your /ALUN channel ID
    "vip": "-1003295571464",      # replace with your /VIP channel ID
}
# --------------------------------------------------

def create_invite_link(channel_id):
    expire_date = int(time.time()) + EXPIRE_SECONDS
    payload = {
        "chat_id": channel_id,
        "expire_date": expire_date,
        "member_limit": MEMBER_LIMIT
    }
    r = requests.post(f"{TG_API}/createChatInviteLink", json=payload, timeout=10)
    j = r.json()
    if not j.get("ok"):
        logging.error("createChatInviteLink failed: %s", j)
        raise Exception("Failed to create invite link")
    return j["result"]["invite_link"]

def revoke_link(channel_id, link):
    payload = {"chat_id": channel_id, "invite_link": link}
    try:
        requests.post(f"{TG_API}/revokeChatInviteLink", json=payload, timeout=10)
    except Exception as e:
        logging.exception("Failed to revoke link: %s", e)

# ---------------- COMMAND HANDLER -----------------
@bot.message_handler(commands=list(CHANNEL_MAP.keys()))
def handle_multi_channel(message):
    cmd = message.text.strip().lstrip("/").lower()
    chat_id = message.chat.id
    channel_id = CHANNEL_MAP.get(cmd)

    if not channel_id:
        bot.reply_to(message, "⚠️ Unknown command or channel not configured.")
        return

    try:
        link = create_invite_link(channel_id)
    except Exception as e:
        logging.exception("Error creating invite link")
        bot.send_message(chat_id, "⚠️ Sorry, couldn't create an invite link right now.")
        return

    bot.send_message(chat_id, f"🔗 <b>Private invite link</b> for <code>/{cmd}</code>:\n\n{link}\n\n⏳ Valid for {EXPIRE_SECONDS} seconds.")

    def revoke_later():
        time.sleep(EXPIRE_SECONDS)
        revoke_link(channel_id, link)
        try:
            bot.send_message(chat_id, f"⏳ The /{cmd} invite link has expired.")
        except Exception:
            pass

    threading.Thread(target=revoke_later, daemon=True).start()

# --------------------------------------------------
@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.send_message(message.chat.id,
        "👋 Welcome! Use commands below to get channel invite links:\n\n" +
        "\n".join([f"/{k}" for k in CHANNEL_MAP.keys()])
    )

# --- Health Check for Koyeb ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_server():
    server = HTTPServer(("0.0.0.0", int(os.getenv("PORT", "8080"))), HealthCheckHandler)
    server.serve_forever()

# --- Start ---
if __name__ == '__main__':
    threading.Thread(target=run_server, daemon=True).start()
    logging.info("✅ Bot started with multiple-channel support.")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)