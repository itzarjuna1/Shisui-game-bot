# ============================================
# File: /plugins/clan.py
# ============================================

from pyrogram import Client, filters
from database.mongo import clans, users
from .utilities import blockquote, mention
from core.config import Config
import time

app: Client = Client._global_client if hasattr(Client, "_global_client") else None

# -----------------------------
# Create clan command
# -----------------------------
@Client.on_message(filters.command("createclan"))
async def create_clan(client, message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply_text(blockquote("> Provide a clan name. Example: /createclan Sakura"))

    name = args[1].strip()[:30]
    owner = message.from_user.id

    existing = await clans.find_one({"owner": owner})
    if existing:
        return await message.reply_text(blockquote("> You already own a clan."))

    clan_doc = {
        "name": name,
        "owner": owner,
        "members": [owner],
        "balance": 0,
        "created": int(time.time())
    }

    await clans.insert_one(clan_doc)
    await message.reply_text(
        blockquote(f"> The clan **{name}** has been formed. Lead it with honor!"),
    )


# -----------------------------
# Clan info command
# -----------------------------
@Client.on_message(filters.command("clan"))
async def clan_info(client, message):
    user_id = message.from_user.id
    doc = await clans.find_one({"members": user_id})
    if not doc:
        return await message.reply_text(blockquote("> You are not in a clan."))

    owner_user = await client.get_users(doc["owner"])
    text = (
        f"> Clan: **{doc['name']}**\n"
        f"> Owner: {owner_user.first_name}\n"
        f"> Members: {len(doc['members'])}\n"
        f"> Bank: {doc.get('balance', 0)} coins"
    )
    await message.reply_text(blockquote(text))


# -----------------------------
# Gift coins within clan
# -----------------------------
@Client.on_message(filters.command("gift") & ~filters.private)
async def clan_gift(client, message):
    if len(message.command) < 3:
        return await message.reply_text(blockquote("> Usage: /gift @user amount"))

    try:
        username = message.command[1]
        amount = int(message.command[2])
    except:
        return await message.reply_text(blockquote("> Invalid usage."))

    try:
        u = await client.get_users(username)
    except:
        return await message.reply_text(blockquote("> User not found."))

    giver = message.from_user.id
    giver_doc = await users.find_one({"_id": giver}) or {}

    if giver_doc.get("balance", 0) < amount:
        return await message.reply_text(blockquote("> Insufficient funds."))

    await users.update_one({"_id": giver}, {"$inc": {"balance": -amount}}, upsert=True)
    await users.update_one({"_id": u.id}, {"$inc": {"balance": amount}}, upsert=True)

    await message.reply_text(blockquote(f"> You gifted **{amount}** coins to {u.first_name}."))
