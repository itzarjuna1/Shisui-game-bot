from pyrogram import Client, filters
from pyrogram.types import Message

from decorators.admin_check import admin_only
from decorators.voice_chat_check import require_voice_chat
from plugins.music import player


# -----------------------------
# /stop
# -----------------------------
@Client.on_message(filters.command("stop") & ~filters.private)
@admin_only
@require_voice_chat
async def stop_cmd(client: Client, message: Message):
    chat_id = message.chat.id

    try:
        is_active = await player.is_active(chat_id)
        if not is_active:
            return await message.reply_text("> ⏹ Nothing is playing to stop.", quote=True)

        ok = await player.stop(chat_id)
        if ok:
            await message.reply_text("> ⏹ Music stopped and queue cleared.", quote=True)
        else:
            await message.reply_text("> ❌ Could not stop.", quote=True)

    except Exception as e:
        await message.reply_text(f"> ❌ Error occurred: `{e}`", quote=True)
