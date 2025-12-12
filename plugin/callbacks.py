from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from YukkiMusic import app
from utils.player import MusicPlayer  # Adjust path to your player
# If you have different structure, tell me, I will fix imports.


@app.on_callback_query(filters.regex("pause"))
async def pause_callback(_, query: CallbackQuery):
    video_id = query.data.split("[")[1].replace("]", "")
    await MusicPlayer.pause_music(query.message.chat.id)
    await query.answer("⏸ Music Paused")


@app.on_callback_query(filters.regex("resume"))
async def resume_callback(_, query: CallbackQuery):
    video_id = query.data.split("[")[1].replace("]", "")
    await MusicPlayer.resume_music(query.message.chat.id)
    await query.answer("▶️ Music Resumed")


@app.on_callback_query(filters.regex("skip"))
async def skip_callback(_, query: CallbackQuery):
    video_id = query.data.split("[")[1].replace("]", "")
    await MusicPlayer.skip_music(query.message.chat.id)
    await query.answer("⏭ Skipped!")


@app.on_callback_query(filters.regex("stop"))
async def stop_callback(_, query: CallbackQuery):
    await MusicPlayer.stop_music(query.message.chat.id)
    await query.answer("⏹ Stopped!")
