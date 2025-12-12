from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from decorators.admin_check import admin_only
from decorators.voice_chat_check import require_voice_chat
from main import MUSIC_QUEUE, CURRENT_PLAYING, pytgcalls, AudioPiped
from plugins.music import youtube, spotify, soundcloud, apple_music, resso
import asyncio

OWNER_NAME = "YourName"

# Platform detection helper
def detect_platform(url: str):
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    elif "spotify.com" in url:
        return "spotify"
    elif "soundcloud.com" in url:
        return "soundcloud"
    elif "music.apple.com" in url:
        return "apple"
    elif "resso.com" in url:
        return "resso"
    else:
        return "youtube"  # fallback search

@Client.on_message(filters.command("play") & ~filters.private)
@admin_only
@require_voice_chat
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

        # Detect platform
        platform = detect_platform(song)
        if platform == "youtube":
            info = youtube.get_youtube_audio(song)
        elif platform == "spotify":
            info = spotify.get_spotify_track_audio(song)
        elif platform == "soundcloud":
            info = soundcloud.get_soundcloud_audio(song)
        elif platform == "apple":
            info = apple_music.get_apple_music_audio(song, "")  # optional artist arg
        elif platform == "resso":
            info = resso.get_resso_audio(song, "")

        url = info["url"]
        title = info.get("title", "Unknown")
        duration = info.get("duration", 0)

        # Inline buttons
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⏸ Pause", callback_data="pause"),
                InlineKeyboardButton("⏭ Skip", callback_data="skip")
            ],
            [
                InlineKeyboardButton("💬 Support", url="https://t.me/dark_musicsupport"),
                InlineKeyboardButton("📢 Channel", url="https://t.me/dark_musictm")
            ]
        ])

        # Send now playing message
        await message.reply_text(
            f"> 🎵 Now Playing: **{title}**\n> ⏱ Duration: {duration} sec\n> Made by {OWNER_NAME}",
            reply_markup=keyboard
        )

        # Play in voice chat
        try:
            await pytgcalls.join_group_call(chat_id, AudioPiped(url))
            await asyncio.sleep(duration)
        except Exception as e:
            await message.reply_text(f"> Failed to play: {e}")

        MUSIC_QUEUE[chat_id].pop(0)

    CURRENT_PLAYING[chat_id] = False
