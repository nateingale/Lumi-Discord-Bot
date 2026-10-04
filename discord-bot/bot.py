import os

import discord
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

openai_client = OpenAI()

token = os.getenv("DISCORD_TOKEN")
if not token:
    raise RuntimeError(
        "DISCORD_TOKEN is missing. Set it in the environment or in discord-bot/.env."
    )

client = discord.Client(intents=discord.Intents.default())


@client.event
async def on_ready() -> None:
    print(f"Connected as {client.user}")


client.run(token)