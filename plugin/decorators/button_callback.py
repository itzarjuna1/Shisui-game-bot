from pyrogram import Client
from pyrogram.types import CallbackQuery
from main import pytgcalls

@Client.on_callback_query()
async def button_handler(client: Client, query: CallbackQuery):
    chat_id = query.message.chat.id
    data = query.data

    if data == "pause":
        try:
            await pytgcalls.pause_stream(chat_id)
            await query.answer("⏸ Paused")
        except:
            await query.answer("Failed to pause")
    elif data == "resume":
        try:
            await pytgcalls.resume_stream(chat_id)
            await query.answer("▶ Resumed")
    elif data == "skip":
        from main import MUSIC_QUEUE
        if MUSIC_QUEUE.get(chat_id):
            MUSIC_QUEUE[chat_id].pop(0)
            await query.answer("⏭ Skipped")
