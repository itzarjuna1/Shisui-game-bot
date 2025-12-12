# ============================================
# File: /plugins/tsukuyomi.py
# ============================================

from pyrogram import Client, filters
from pyrogram.types import ChatPermissions
from core.config import Config
from .utilities import blockquote

app: Client = Client._global_client if hasattr(Client, "_global_client") else None

@Client.on_message(filters.command(["infinite_tsukuyomi", "tsukuyomi"]) & filters.group)
async def tsukuyomi_cmd(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    member = await client.get_chat_member(chat_id, user_id)
    if not (member.can_manage_chat or member.status == "creator"):
        return await message.reply_text(blockquote("> Only admins may summon the Infinite Tsukuyomi."))

    # Lock the chat
    await client.set_chat_permissions(chat_id, ChatPermissions())
    
    caption = blockquote(
        "> 🌙 The red moon rises…\n"
        "> All minds drift into Mitsuha’s Infinite love drift."
    )

    # Send banner image (from config)
    await message.reply_photo(
        photo=Config.TSUKUYOMI_IMAGE,
        caption=caption
    )
