from pyrogram import Client, filters
from pyrogram.types import Message

from decorators.admin_check import admin_only
from decorators.voice_chat_check import require_voice_chat
from plugins.music import player

app: Client = Client._global_client if hasattr(Client, "_global_client") else None

# -----------------------------
# /skip
# -----------------------------
@Client.on_message(filters.command("skip") & ~filters.private)
@admin_only
@require_voice_chat
async def skip_cmd(client: Client, message: Message):
    chat_id = message.chat.id

    try:
        current = await player.now_playing(chat_id)
        if not current:
            return await message.reply_text("> ▶️ Nothing is playing right now.", quote=True)

        ok = await player.skip(chat_id)
        if ok:
            await message.reply_text("> ⏭ Skipped the current track.", quote=True)
        else:
            await message.reply_text("> ❌ Could not skip right now.", quote=True)
    except Exception as e:
        await message.reply_text(f"> ❌ Error while skipping: {e}", quote=True)
