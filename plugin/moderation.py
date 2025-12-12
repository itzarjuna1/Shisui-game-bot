# ============================================
# File: /plugins/moderation.py
# ============================================

from pyrogram import Client, filters
from pyrogram.types import ChatPermissions
from core.config import Config
from database.mongo import users, gbans
from .utilities import blockquote, mention

app: Client = Client._global_client if hasattr(Client, "_global_client") else None

SUDO_LIST = set(Config.SUDO_USERS or [])

# -----------------------------
# Ban command
# -----------------------------
@Client.on_message(filters.command("ban") & filters.group)
async def ban_cmd(client, message):
    if message.from_user.id not in SUDO_LIST:
        return await message.reply_text(blockquote("> You are not allowed to wield this power."))

    if not message.reply_to_message:
        return await message.reply_text(blockquote("> Reply to a user to ban them."))

    target = message.reply_to_message.from_user
    try:
        await client.ban_chat_member(message.chat.id, target.id)
        await message.reply_text(blockquote(f"> {mention(target.id, target.first_name)} has been banned."))
    except Exception as e:
        await message.reply_text(blockquote(f"> Failed to ban: {e}"))


# -----------------------------
# Mute command
# -----------------------------
@Client.on_message(filters.command("mute") & filters.group)
async def mute_cmd(client, message):
    if message.from_user.id not in SUDO_LIST:
        return await message.reply_text(blockquote("> You are not allowed to wield this power."))

    if not message.reply_to_message:
        return await message.reply_text(blockquote("> Reply to a user to mute them."))

    target = message.reply_to_message.from_user
    try:
        await client.restrict_chat_member(
            message.chat.id,
            target.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        await message.reply_text(blockquote(f"> {mention(target.id, target.first_name)} muted."))
    except Exception as e:
        await message.reply_text(blockquote(f"> Failed to mute: {e}"))


# -----------------------------
# Superban command (global ban)
# -----------------------------
@Client.on_message(filters.command("superban"))
async def superban_cmd(client, message):
    if message.from_user.id not in SUDO_LIST:
        return await message.reply_text(blockquote("> Only sudo users may cast the Superban."))

    if not message.reply_to_message:
        return await message.reply_text(blockquote("> Reply to a user to superban them globally."))

    target = message.reply_to_message.from_user
    await gbans.insert_one({"_id": target.id})

    # Log superban (to logger group)
    try:
        await client.send_message(
            Config.LOGGER_ID,
            blockquote(f"> 🔥 Superban executed on {mention(target.id, target.first_name)}")
        )
    except:
        pass

    await message.reply_text(blockquote(f"> {mention(target.id, target.first_name)} has been globally banned."))


# -----------------------------
# Kick command
# -----------------------------
@Client.on_message(filters.command("kick") & filters.group)
async def kick_cmd(client, message):
    if message.from_user.id not in SUDO_LIST:
        return await message.reply_text(blockquote("> You are not allowed to kick."))

    if not message.reply_to_message:
        return await message.reply_text(blockquote("> Reply to a user to kick them."))

    target = message.reply_to_message.from_user
    try:
        await client.kick_chat_member(message.chat.id, target.id)
        await message.reply_text(blockquote(f"> {mention(target.id, target.first_name)} has been kicked."))
    except Exception as e:
        await message.reply_text(blockquote(f"> Failed to kick: {e}"))
