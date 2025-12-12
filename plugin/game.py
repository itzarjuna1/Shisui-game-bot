# ============================================
# File: /plugins/games.py
# ============================================

from pyrogram import Client, filters
from .utilities import blockquote
import random

app: Client = Client._global_client if hasattr(Client, "_global_client") else None

# -----------------------------
# Kill game
# -----------------------------
@Client.on_message(filters.command("kill") & ~filters.private)
async def kill_cmd(client, message):
    if not message.reply_to_message:
        return await message.reply_text(blockquote("> Reply to a user to kill them (game)."))

    target = message.reply_to_message.from_user
    await message.reply_text(blockquote(f"> {target.first_name} was struck down by unseen blades. ⚔️"))


# -----------------------------
# Love compatibility
# -----------------------------
@Client.on_message(filters.command("love") & ~filters.private)
async def love_cmd(client, message):
    if len(message.command) < 2 or not message.reply_to_message:
        return await message.reply_text(blockquote("> Reply to someone to calculate love percentage."))

    target = message.reply_to_message.from_user
    percent = random.randint(0, 100)
    await message.reply_text(blockquote(f"> ❤️ Love meter between {message.from_user.first_name} and {target.first_name}: {percent}%"))


# -----------------------------
# Couples match
# -----------------------------
@Client.on_message(filters.command("couples") & ~filters.private)
async def couples_cmd(client, message):
    members = [message.from_user.first_name]
    if message.reply_to_message:
        members.append(message.reply_to_message.from_user.first_name)
    else:
        members.append(random.choice(["Sakura","Mikasa","Hinata","Mitsuha","Yuki"]))

    percent = random.randint(0, 100)
    await message.reply_text(blockquote(f"> 💞 Couple check: {members[0]} + {members[1]} = {percent}% compatible."))


# -----------------------------
# Marry command
# -----------------------------
@Client.on_message(filters.command("marry") & ~filters.private)
async def marry_cmd(client, message):
    if not message.reply_to_message:
        return await message.reply_text(blockquote("> Reply to someone to propose marriage."))

    target = message.reply_to_message.from_user
    success = random.random() < 0.7
    if success:
        await message.reply_text(blockquote(f"> 💍 {message.from_user.first_name} is now married to {target.first_name}!"))
    else:
        await message.reply_text(blockquote(f"> ❌ {target.first_name} rejected the proposal from {message.from_user.first_name}."))


# -----------------------------
# Chatfight command
# -----------------------------
@Client.on_message(filters.command("chatfight") & ~filters.private)
async def chatfight_cmd(client, message):
    if not message.reply_to_message:
        return await message.reply_text(blockquote("> Reply to someone to start a chatfight."))

    target = message.reply_to_message.from_user
    moves = ["Punch 🥊", "Kick 🦵", "Shadow Strike 🌑", "Fireball 🔥", "Water Wave 🌊"]
    user_move = random.choice(moves)
    target_move = random.choice(moves)

    result = random.choice(["won", "lost", "draw"])
    await message.reply_text(
        blockquote(
            f"> {message.from_user.first_name} used {user_move}\n"
            f"> {target.first_name} used {target_move}\n"
            f"> Result: {message.from_user.first_name} {result}!"
        )
  )
