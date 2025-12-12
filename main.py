import asyncio
from core.client import start_clients, stop_clients
from pyrogram import idle


async def main():
    # Start bot & assistant
    bot, assistant = await start_clients()

    print("[MITSUHA] All systems online. Awaiting commands...")

    # Keep alive until Ctrl+C
    await idle()

    # Shutdown sequence
    await stop_clients()
    print("[MITSUHA] Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
