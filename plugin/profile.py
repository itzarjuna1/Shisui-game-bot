# ============================================
# File: /plugins/profile.py
# ============================================

from pyrogram import Client, filters
from .utilities import blockquote

app: Client = Client._global_client if hasattr(Client, "_global_client") else None

# -----------------------------
# Profile command
# -----------------------------
@Client.on_message(filters.command("profile"))
async def profile_cmd(client, message):
    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    username = f"@{user.username}" if user.username else "None"
    
    text = (
        f"> 👤 Name: {user.first_name}\n"
        f"> 🆔 ID: `{user.id}`\n"
        f"> 📛 Username: {username}"
    )
    await message.reply_text(blockquote(text))
