from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from plugins.music import player
from decorators.voice_chat_check import require_voice_chat


# -----------------------------
# /nowplaying  |  /np
# -----------------------------
@Client.on_message(filters.command(["nowplaying", "np"]) & ~filters.private)
@require_voice_chat
async def nowplaying_cmd(client: Client, message: Message):
    chat_id = message.chat.id

    try:
        track = await player.now_playing(chat_id)
        if not track:
            return await message.reply_text("> 🎧 No track is currently playing.", quote=True)

        # Generate progress bar
        position = await player.get_position(chat_id)
        duration = track.duration_sec
        filled = int((position / duration) * 20) if duration else 0
        bar = "▰" * filled + "▱" * (20 - filled)

        # Build the text
        text = (
            f"**🎶 Now Playing**\n\n"
            f"**🎵 Title:** {track.title}\n"
            f"**⏱ Duration:** `{track.duration}`\n"
            f"**👤 Requested by:** {track.requested_by}\n\n"
            f"**Progress:**\n"
            f"`{bar}`\n"
            f"`{player.format_time(position)} / {track.duration}`"
        )

        # Inline buttons
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⏸ Pause", callback_data="music_pause"),
                    InlineKeyboardButton("▶️ Resume", callback_data="music_resume"),
                ],
                [
                    InlineKeyboardButton("⏭ Skip", callback_data="music_skip"),
                    InlineKeyboardButton("⏹ Stop", callback_data="music_stop"),
                ]
            ]
        )

        await message.reply_photo(
            photo=track.thumbnail,
            caption=text,
            reply_markup=keyboard
        )

    except Exception as e:
        await message.reply_text(
            f"> ❌ Could not show now-playing: `{e}`",
            quote=True
        )
