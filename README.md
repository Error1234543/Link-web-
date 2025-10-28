# Secure Invite Bot (Auto-expiring Telegram Channel Link)

**Bot username:** @Indcyberbot
**Channel ID:** -1003295571464
**Behavior:** When a user sends `/start` to the bot, it will generate a one-time invite link to the above channel, send it to the user, and revoke the link after 20 seconds (default). The bot does not store your BOT_TOKEN in code; set it as an environment variable.

---

## Files in this repo
- `bot.py` - main bot code (uses environment variables)
- `requirements.txt` - Python dependencies
- `Dockerfile` - simple container image to deploy on Koyeb or other platforms
- `README.md` - this file

---

## Setup (Local / Termux)

1. Place files in a folder and open terminal there.
2. Install Python and pip if not present.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set environment variables (DO NOT share your BOT_TOKEN):
   ```bash
   export BOT_TOKEN="YOUR_NEW_BOT_TOKEN"
   export CHANNEL_ID="-1003295571464"
   export EXPIRE_SECONDS="20"   # optional
   ```
5. Run:
   ```bash
   python bot.py
   ```

---
## Deploy on Koyeb (recommended)

1. Push this repository to GitHub.
2. On Koyeb, create a new service and connect your GitHub repo (or use the image build).
3. Provide environment variables in Koyeb dashboard:
   - `BOT_TOKEN` = your bot token (keep private)
   - `CHANNEL_ID` = -1003295571464
   - (optional) `EXPIRE_SECONDS` = 20
4. Deploy. The service will run the bot and handle `/start` requests.

---
## Important Security Notes
- **Regenerate your bot token** in @BotFather and keep the new token private.
- Make sure the bot is an **administrator** in your channel with permission to create invite links.
- Do not post your BOT_TOKEN publicly.
- If you suspect token compromise, revoke it immediately via @BotFather.

---
## Troubleshooting
- If `createChatInviteLink` fails, ensure the bot is admin in the channel and has the required permissions.
- If users don't receive messages, they may have blocked the bot or not allowed messages.
- For Koyeb, ensure the service has outbound network access.

