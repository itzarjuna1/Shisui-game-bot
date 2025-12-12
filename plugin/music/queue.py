from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from plugins.music import player
from decorators.voice_chat_check import require_voice_chat


# -----------------------------
# /queue
# -----------------------------
@Client.on_message(filters.command("queue") & ~filters.private)
@require_voice_chat
async def queue_cmd(client: Client, message: Message):
    chat_id = message.chat.id

    try:
        queue_list = await player.get_queue(chat_id)

        if not queue_list:
            return await message.reply_text(
                "> 📭 The queue is empty.",
                quote=True
            )

        text = "**🎧 Current Queue:**\n\n"

        for index, track in enumerate(queue_list, start=1):
            text += (
                f"**{index}.** 🎵 {track.title}\n"
                f"⏱ `{track.duration}` — 👤 {track.requested_by}\n\n"
            )

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⏭ Skip", callback_data="music_skip"),
                    InlineKeyboardButton("⏹ Stop", callback_data="music_stop")
                ]
            ]
        )

        await message.reply_text(text, reply_markup=keyboard, quote=True)

    except Exception as e:
        await message.reply_text(
            f"> ❌ Error showing queue: `{e}`",
            quote=True
        )
