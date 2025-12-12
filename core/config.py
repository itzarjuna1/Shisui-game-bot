import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ---- TELEGRAM ----
    API_ID = int(os.getenv("API_ID", 12345))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")

    # ---- ASSISTANT (FOR VOICE CHAT MUSIC) ----
    ASSISTANT_SESSION = os.getenv("ASSISTANT_SESSION", "")

    # ---- DATABASE ----
    DB_URL = os.getenv("DB_URL", "mongodb+srv://...")

    # ---- OWNERS & SUDO ----
    OWNER_ID = int(os.getenv("OWNER_ID", 0))
    SUDO_USERS = list(map(int, os.getenv("SUDO_USERS", "0").split()))

    # ---- LOG CHANNEL ----
    LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", 0))

    # ---- MUSIC SETTINGS ----
    YT_COOKIES = "music/cookies.txt"   # cookie path
    MAX_DURATION = 900                 # 15 minutes maximum song
    CLEANMODE = True                   # auto delete messages

    # ---- BOT SETTINGS ----
    BOT_NAME = "Mitsuha Game Bot"
    BOT_USERNAME = os.getenv("BOT_USERNAME", "mitsuha_bot")
  
