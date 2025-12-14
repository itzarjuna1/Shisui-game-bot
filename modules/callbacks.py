from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from config import OWNER_NAME
from modules.player import (
    pause_stream,
    resume_stream,
    skip_stream,
    stop_stream,
    toggle_loop
)

# -------------------- PAUSE --------------------
@Client.on_callback_query(filters.regex("^pause_"))
async def pause_cb(client: Client, query: CallbackQuery):
    await pause_stream(query.message.chat.id)
    await query.answer("⏸ Music Paused")
    await query.message.edit_caption(
        query.message.caption + "\n\n⏸ **Paused**"
    )


# -------------------- RESUME --------------------
@Client.on_callback_query(filters.regex("^resume_"))
async def resume_cb(client: Client, query: CallbackQuery):
    await resume_stream(query.message.chat.id)
    await query.answer("▶️ Music Resumed")
    await query.message.edit_caption(
        query.message.caption.replace("⏸ **Paused**", "▶️ **Playing**")
    )


# -------------------- SKIP --------------------
@Client.on_callback_query(filters.regex("^skip_"))
async def skip_cb(client: Client, query: CallbackQuery):
    await skip_stream(query.message.chat.id)
    await query.answer("⏭ Skipped")


# -------------------- STOP --------------------
@Client.on_callback_query(filters.regex("^stop_"))
async def stop_cb(client: Client, query: CallbackQuery):
    await stop_stream(query.message.chat.id)
    await query.answer("⏹ Music Stopped")
    await query.message.delete()


# -------------------- LOOP --------------------
@Client.on_callback_query(filters.regex("^loop_"))
async def loop_cb(client: Client, query: CallbackQuery):
    state = await toggle_loop(query.message.chat.id)
    await query.answer(f"🔁 Loop {'Enabled' if state else 'Disabled'}", show_alert=True)


# -------------------- CLOSE PANEL --------------------
@Client.on_callback_query(filters.regex("^close_panel$"))
async def close_cb(client: Client, query: CallbackQuery):
    await query.message.delete()


# -------------------- OWNER INFO --------------------
@Client.on_callback_query(filters.regex("^owner_info$"))
async def owner_cb(client: Client, query: CallbackQuery):
    await query.answer(
        f"✨ Made with ❤️ by {OWNER_NAME}",
        show_alert=True
    )
