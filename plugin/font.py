# ============================================
# File: /plugins/font.py
# ============================================

from pyrogram import Client, filters
from pyrogram.types import Message
from .utilities import mitsuha_font, blockquote

app: Client = Client._global_client if hasattr(Client, "_global_client") else None

@Client.on_message(filters.command("font"))
async def font_cmd(client: Client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply_text(blockquote("> Please provide text to stylize. Example: /font Hello"))

    text = args[1].strip()
    styled_text = mitsuha_font(text)
    await message.reply_text(blockquote(styled_text))
