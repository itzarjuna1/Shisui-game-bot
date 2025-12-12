# ============================================
# File: /plugins/economy.py
# ============================================

from pyrogram import Client, filters
from database.mongo import users
from .utilities import blockquote
import time, random

app: Client = Client._global_client if hasattr(Client, "_global_client") else None

DEFAULTS = {
    "daily_amount": 500,
    "work_cooldown": 3600,
    "rob_cooldown": 600,
}

# -----------------------------
# Balance command
# -----------------------------
@Client.on_message(filters.command("balance"))
async def balance_cmd(client, message):
    user_id = message.from_user.id
    doc = await users.find_one({"_id": user_id}) or {}
    bal = doc.get("balance", 0)
    await message.reply_text(blockquote(f"> 💳 Balance: {bal} coins"))


# -----------------------------
# Daily reward command
# -----------------------------
@Client.on_message(filters.command("daily"))
async def daily_cmd(client, message):
    user_id = message.from_user.id
    now = int(time.time())
    doc = await users.find_one({"_id": user_id}) or {}
    last = doc.get("daily_ts", 0)

    if now - last < 24*3600:
        return await message.reply_text(blockquote("> You have already claimed your daily reward."))

    amount = DEFAULTS["daily_amount"]
    await users.update_one(
        {"_id": user_id},
        {"$inc": {"balance": amount}, "$set": {"daily_ts": now}},
        upsert=True
    )
    await message.reply_text(blockquote(f"> You received **{amount}** coins for today 🌸"))


# -----------------------------
# Work command
# -----------------------------
@Client.on_message(filters.command("work"))
async def work_cmd(client, message):
    user_id = message.from_user.id
    now = int(time.time())
    doc = await users.find_one({"_id": user_id}) or {}
    last = doc.get("work_ts", 0)

    if now - last < DEFAULTS["work_cooldown"]:
        return await message.reply_text(blockquote("> You need to rest before working again."))

    jobs = [("Mage",200,500),("Guard",50,200),("Courier",100,400),("Hacker",250,1000)]
    job = random.choice(jobs)
    earned = random.randint(job[1], job[2])

    await users
