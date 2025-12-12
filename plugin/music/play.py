from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from decorators.admin_check import admin_only
from main import MUSIC_QUEUE, CURRENT_PLAYING, pytgcalls
import asyncio
import yt_dlp as ytdlp
import os

OWNER_NAME = "YourName"

@Client.on_message(filters.command("play") & ~filters.private)
@admin_only
async def play_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply_text("> Provide a song name or link. Example: /play Shape of You")

    query = args[1]

    if chat_id not in MUSIC_QUEUE:
        MUSIC_QUEUE[chat_id] = []

    MUSIC_QUEUE[chat_id].append(query)
    await message.reply_text(f"> Added to queue: {query}")

    if chat_id not in CURRENT_PLAYING or not CURRENT_PLAYING[chat_id]:
        CURRENT_PLAYING[chat_id] = True
        await process_queue(client, chat_id, message)

async def process_queue(client: Client, chat_id: int, message: Message):
    while MUSIC_QUEUE.get(chat_id):
        song = MUSIC_QUEUE[chat_id][0]
        # Download with yt-dlp
        os.makedirs("downloads", exist_ok=True)
        file_path = f"downloads/{chat_id}.mp3"
        ydl_opts = {
            "format": "bestaudio",
            "outtmpl": file_path,
            "quiet": True,
            "noplaylist": True,
        }
        with ytdlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(song, download=True)

        title = info.get("title", "Unknown")
        duration = info.get("duration", 0)

        # Inline buttons: Pause, Skip, Support, Channel
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⏸ Pause", callback_data="pause"),
                InlineKeyboardButton("⏭ Skip", callback_data="skip")
            ],
            [
                InlineKeyboardButton("💬 Support", url="https://t.me/YourSupportGroup"),
                InlineKeyboardButton("📢 Channel", url="https://t.me/YourChannel")
            ]
        ])
        # Send now playing message
        await message.reply_text(
            f"> 🎵 Now Playing: **{title}**\n> ⏱ Duration: {duration} sec\n> Made by {OWNER_NAME}",
            reply_markup=keyboard
        )

        # Play in VC
        try:
            await pytgcalls.join_group_call(chat_id, AudioPiped(file_path))
            await asyncio.sleep(duration)
        except Exception as e:
            await message.reply_text(f"> Failed to play: {e}")

        MUSIC_QUEUE[chat_id].pop(0)
    CURRENT_PLAYING[chat_id] = False
