from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from plugins.music import player
from decorators.admin_check import admin_only
from decorators.voice_chat_check import require_voice_chat


@Client.on_message(filters.command("play") & ~filters.private)
@admin_only
@require_voice_chat
async def play_command(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # Parse search query or link
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply_text(
            "> Provide a song name or link.\n> Example: `/play Arcade`",
            quote=True
        )

    query = args[1]

    # Enqueue using engine
    track = await player.enqueue(chat_id, query, user_id)

    # Inline buttons
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎧 Queue", callback_data="music_queue"),
            InlineKeyboardButton("⏭ Skip", callback_data="music_skip")
        ],
        [
            InlineKeyboardButton("💬 Support", url="https://t.me/YourSupportGroup"),
            InlineKeyboardButton("📢 Channel", url="https://t.me/YourChannel")
        ]
    ])

    await message.reply_text(
        f"> 🎵 **Added to Queue**\n"
        f"> **Title:** {track.title}\n"
        f"> ⏱ Duration: {track.duration} sec\n"
        f"> 👤 Requested by: {message.from_user.mention}",
        reply_markup=keyboard,
        quote=True
    )
