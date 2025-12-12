from pyrogram import Client
from motor.motor_asyncio import AsyncIOMotorClient
from .config import Config


# ------------------------------
# DATABASE CONNECTION
# ------------------------------
db = AsyncIOMotorClient(Config.DB_URL)
mongodb = db["MitsuhaGame"]     # Database name


# ------------------------------
# MAIN BOT CLIENT
# ------------------------------
bot = Client(
    name=Config.BOT_NAME,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins={"root": "plugins"}
)


# ------------------------------
# ASSISTANT CLIENT FOR MUSIC
# ------------------------------
assistant = Client(
    name="assistant",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    session_string=Config.ASSISTANT_SESSION
)


# ------------------------------
# STARTUP LOGS
# ------------------------------
async def start_clients():
    print("[MITSUHA] Starting bot & assistant...")

    await bot.start()
    await assistant.start()

    print(f"[MITSUHA] Bot: @{Config.BOT_USERNAME} running.")
    print("[MITSUHA] Assistant account connected.")

    return bot, assistant


async def stop_clients():
    print("[MITSUHA] Stopping clients...")
    await bot.stop()
    await assistant.stop()
