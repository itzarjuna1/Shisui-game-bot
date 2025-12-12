from pyrogram import Client, filters
from pyrogram.types import Message

from decorators.admin_check import admin_only
from decorators.voice_chat_check import require_voice_chat
from plugins.music import player


# -----------------------------
# /pause
# -----------------------------
@Client.on_message(filters.command("pause") & ~filters.private)
@admin_only
@require_voice_chat
async def pause_cmd(client: Client, message: Message):
    chat_id = message.chat.id

    try:
        is_playing = await player.is_playing(chat_id)
        if not is_playing:
            return await message.reply_text("> ▶️ Nothing is playing to pause.", quote=True)

        done = await player.pause(chat_id)
        if done:
            await message.reply_text("> ⏸ Music paused.", quote=True)
        else:
            await message.reply_text("> ❌ Could not pause.", quote=True)

    except Exception as e:
        await message.reply_text(f"> ❌ Error: `{e}`", quote=True)
