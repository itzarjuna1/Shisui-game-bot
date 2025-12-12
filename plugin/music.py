from pyrogram import Client, filters
from pyrogram.types import Message
from config import BOT_NAME
import asyncio
import youtube_dl
import random

# Placeholder for assistant session & music queue
MUSIC_QUEUE = {}

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

    # Initialize queue for chat if not exists
    if chat_id not in MUSIC_QUEUE:
        MUSIC_QUEUE[chat_id] = []

    # Add song to queue
    MUSIC_QUEUE[chat_id].append(query)
    await message.reply_text(f"> Added to queue: {query}")

    # If more than one song, don't start another
    if len(MUSIC_QUEUE[chat_id]) > 1:
        return

    await process_queue(client, chat_id, message)

# -----------------------------
# Process queue
# -----------------------------
async def process_queue(client: Client, chat_id: int, message: Message):
    while MUSIC_QUEUE[chat_id]:
        song = MUSIC_QUEUE[chat_id][0]
        try:
            await message.reply_text(f"> Now playing: {song} 🎵")
            # Download & play using youtube_dl or other engines
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(song, download=False)
                url = info['url']
                # Here, integrate with voice chat or streaming assistant ID
                # Example: await play_audio_assistant(chat_id, url)
                await asyncio.sleep(5)  # simulate playing duration
        except Exception as e:
            await message.reply_text(f"> Failed to play: {e}")
        finally:
            MUSIC_QUEUE[chat_id].pop(0)
            if MUSIC_QUEUE[chat_id]:
                await message.reply_text(f"> Next up: {MUSIC_QUEUE[chat_id][0]}")
