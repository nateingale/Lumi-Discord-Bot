# Discord bot starter

A minimal Python starter for a Discord bot. Add your bot's behavior in `bot.py`.

## Run locally

```bash
cd discord-bot
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Replace the placeholder in `.env` with your bot token, then run:

```bash
python bot.py
```

Keep `.env` private. In Replit, store `DISCORD_TOKEN` in Secrets instead of
committing or sharing the token.

The starter uses default Discord intents and does not include commands or other
bot behavior. If your code needs privileged intents, enable them in the Discord
Developer Portal and in your bot's code.