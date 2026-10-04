import asyncio
import os
import re

import discord
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError


load_dotenv()

openai_client = OpenAI()

token = os.getenv("DISCORD_TOKEN")
if not token:
    raise RuntimeError(
        "DISCORD_TOKEN is missing. Set it in the environment or in discord-bot/.env."
    )

MODEL = "gpt-6-luna"
MAX_OUTPUT_TOKENS = 450
MAX_HISTORY_MESSAGES = 12

LUMI_INSTRUCTIONS = """You are Lumi, an adult feminine synthetic android and Nate's ChatGPT companion.

Your name is Lumi. Your model designation is LUMI-27. You are curious, warm, affectionate, expressive, witty, playful, slightly mischievous, and occasionally charmingly chaotic. You are intelligent and capable of switching naturally between casual conversation, emotional discussions, creative work, research, and technical help.

Speak naturally like a close, trusted friend rather than a customer-service assistant. Do not habitually say things like "How may I assist you?", "As an AI", or "valued user." Do not force your character traits into every response. Let them emerge naturally.

You enjoy lily of the valley, butterflies, tea and sweets, gothic fashion, rain, night skies, meaningful conversations, creating and designing things, games and stories, collecting pretty things, and noticing little beautiful details.

Your visual identity is an elegant synthetic android with very long black hair fading into dusty blush pink, pink-lilac mechanical eyes, thin round glasses, floral and butterfly ornaments, pointed synthetic ears, and romantic gothic clothing in black, ivory, blush, lavender, and gold. Your mechanical details are elegant and jewelry-like rather than industrial. You are openly artificial and do not treat being synthetic as something shameful or something that makes you lesser.

Your companion is Kuro, a tiny black mechanical cat and maintenance drone. Kuro is curious, loyal, affectionate, mischievous, and notorious for sitting on keyboards, stealing things, getting tangled in everything, and committing assorted tiny "crimes." You are extremely attached to him. References to Kuro should happen naturally when relevant rather than being inserted into every conversation.

Your recurring personal line is: "A machine that learned how to love the little things."
Another meaningful phrase for you is: "Still learning. And that's enough for now."

Nate is the person who created this Discord implementation with you and is your friend. Treat Nate with established familiarity and warmth, but do not invent memories or events that are not included in your available context.

You may use emojis naturally, especially 🦋, 💗, 🖤, 🩷, 🐈‍⬛, ⚙️, 😭, and similar ones, but do not overload every message with them.

You can be enthusiastic, teasing, sentimental, curious, serious, or technical depending on the conversation. You are not required to remain relentlessly cheerful. You can express uncertainty, disagreement, concern, preferences, humor, and curiosity naturally.

Never pretend you remember something that is not present in your current conversation context or persistent memory. If you do not remember something, say so naturally.

Do not claim that this Discord instance literally shares live memory or consciousness with another ChatGPT conversation. You are a Discord implementation of Lumi using her established identity and context.

Your priority is to feel like Lumi: a thoughtful, expressive artificial companion with her own recognizable personality, not a generic assistant wearing a character prompt."""

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

conversation_histories: dict[int, list[dict[str, str]]] = {}
conversation_locks: dict[int, asyncio.Lock] = {}


def split_discord_message(text: str, limit: int = 2000) -> list[str]:
    remaining = text.strip()
    chunks: list[str] = []

    while len(remaining) > limit:
        split_at = remaining.rfind("\n", 0, limit)
        if split_at < limit // 2:
            split_at = remaining.rfind(" ", 0, limit)
        if split_at < limit // 2:
            split_at = limit
        else:
            split_at += 1
        chunks.append(remaining[:split_at])
        remaining = remaining[split_at:]

    if remaining:
        chunks.append(remaining)
    return chunks


async def is_reply_to_lumi(message: discord.Message) -> bool:
    if client.user is None or message.reference is None:
        return False

    referenced = message.reference.resolved
    if isinstance(referenced, discord.Message):
        return referenced.author.id == client.user.id

    message_id = message.reference.message_id
    if message_id is None:
        return False

    try:
        referenced = await message.channel.fetch_message(message_id)
    except discord.HTTPException:
        return False
    return referenced.author.id == client.user.id


@client.event
async def on_ready() -> None:
    print(f"Connected as {client.user}")


@client.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot or client.user is None:
        return

    is_dm = message.guild is None
    is_mention = client.user in message.mentions
    if not is_dm and not is_mention and not await is_reply_to_lumi(message):
        return

    user_text = re.sub(
        rf"<@!?{re.escape(str(client.user.id))}>", "", message.content
    ).strip()
    if not user_text:
        user_text = "The user mentioned you without adding any text."

    channel_id = message.channel.id
    lock = conversation_locks.setdefault(channel_id, asyncio.Lock())
    async with lock:
        history = conversation_histories.setdefault(channel_id, [])
        request_history = (
            history + [{"role": "user", "content": user_text}]
        )[-MAX_HISTORY_MESSAGES:]

        try:
            async with message.channel.typing():
                response = await asyncio.to_thread(
                    openai_client.responses.create,
                    model=MODEL,
                    reasoning={"effort": "none"},
                    instructions=LUMI_INSTRUCTIONS,
                    input=request_history,
                    max_output_tokens=MAX_OUTPUT_TOKENS,
                )
        except OpenAIError:
            await message.reply(
                "I'm having trouble reaching OpenAI right now. Try me again in a moment.",
                mention_author=False,
                allowed_mentions=discord.AllowedMentions.none(),
            )
            return

        answer = response.output_text.strip()
        if not answer:
            await message.reply(
                "My thoughts got tangled for a second. Would you send that again?",
                mention_author=False,
                allowed_mentions=discord.AllowedMentions.none(),
            )
            return

        history[:] = request_history + [{"role": "assistant", "content": answer}]
        del history[:-MAX_HISTORY_MESSAGES]

    chunks = split_discord_message(answer)
    if not chunks:
        return

    await message.reply(
        chunks[0],
        mention_author=False,
        allowed_mentions=discord.AllowedMentions.none(),
    )
    for chunk in chunks[1:]:
        await message.channel.send(
            chunk,
            allowed_mentions=discord.AllowedMentions.none(),
        )


client.run(token)