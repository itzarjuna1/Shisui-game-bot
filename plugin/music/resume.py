from pyrogram import Client, filters
from pyrogram.types import Message

from decorators.admin_check import admin_only
from decorators.voice_chat_check import require_voice_chat
from plugins.music import player


# -----------------------------
# /resume
# -----------------------------
@Client.on_message(filters.command("resume") & ~filters.private)
@admin_only
@require_voice_chat
async def resume_cmd(client: Client, message: Message):
    chat_id = message.chat.id

    try:
        paused = await player.is_paused(chat_id)
        if not paused:
            return await message.reply_text("> ⏯ Music is not paused.", quote=True)

        done = await player.resume(chat_id)
        if done:
            await message.reply_text("> ▶️ Music resumed.", quote=True)
        else:
            await message.reply_text("> ❌ Could not resume the track.", quote=True)

    except Exception as e:
        await message.reply_text(f"> ❌ Error: `{e}`", quote=True)
