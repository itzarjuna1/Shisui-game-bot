from pyrogram import Client, filters
from pyrogram.types import Message
from config import BOT_NAME
import asyncio
import youtube_dl
import random

MUSIC_QUEUE = {}
CURRENT_PLAYING = {}

app: Client = Client._global_client if hasattr(Client, "_global_client") else None

# -----------------------------
# /play command
# -----------------------------
@Client.on_message(filters.command("play") & ~filters.private)
async def play_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        return await message.reply_text("> Provide a song name or link. Example: /play Shape of You")

    query = args[1]

    # Initialize queue for chat
    if chat_id not in MUSIC_QUEUE:
        MUSIC_QUEUE[chat_id] = []

    MUSIC_QUEUE[chat_id].append(query)
    await message.reply_text(f"> Added to queue: {query}")

    if chat_id not in CURRENT_PLAYING or not CURRENT_PLAYING[chat_id]:
        CURRENT_PLAYING[chat_id] = True
        await process_queue(client, chat_id, message)

# -----------------------------
# /skip command
# -----------------------------
@Client.on_message(filters.command("skip") & ~filters.private)
async def skip_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    if MUSIC_QUEUE.get(chat_id):
        MUSIC_QUEUE[chat_id].pop(0)
        await message.reply_text("> Skipped current song.")
        if MUSIC_QUEUE[chat_id]:
            await process_queue(client, chat_id, message)
    else:
        await message.reply_text("> No songs in queue.")

# -----------------------------
# /stop command
# -----------------------------
@Client.on_message(filters.command("stop") & ~filters.private)
async def stop_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    MUSIC_QUEUE[chat_id] = []
    CURRENT_PLAYING[chat_id] = False
    await message.reply_text("> Music stopped and queue cleared.")

# -----------------------------
# Queue processing
# -----------------------------
async def process_queue(client: Client, chat_id: int, message: Message):
    while MUSIC_QUEUE.get(chat_id):
        song = MUSIC_QUEUE[chat_id][0]
        try:
            await message.reply_text(f"> Now playing: {song} 🎵")
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(song, download=False)
                url = info['url']
                # Integrate with assistant voice chat here
                await asyncio.sleep(5)  # Simulate song playing
        except Exception as e:
            await message.reply_text(f"> Failed to play: {e}")
        finally:
            MUSIC_QUEUE[chat_id].pop(0)
    CURRENT_PLAYING[chat_id] = False
