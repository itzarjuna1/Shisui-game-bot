from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from core.config import Config

app: Client = Client._global_client if hasattr(Client, "_global_client") else None

# -----------------------------
# Callback query handler
# -----------------------------
@Client.on_callback_query()
async def callback_handler(client, callback_query):
    data = callback_query.data
    chat_id = callback_query.message.chat.id

    # Games menu
    if data == "menu_games":
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("⚔️ Kill", callback_data="game_kill"),
                 InlineKeyboardButton("💥 Fight", callback_data="game_fight")],
                [InlineKeyboardButton("⬅️ Back", callback_data="menu_main")]
            ]
        )
        await callback_query.message.edit_text("> ⚔️ Choose your game:", reply_markup=keyboard)

    # Economy menu
    elif data == "menu_economy":
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("💰 Balance", callback_data="eco_balance"),
                 InlineKeyboardButton("💎 Daily Reward", callback_data="eco_daily")],
                [InlineKeyboardButton("⬅️ Back", callback_data="menu_main")]
            ]
        )
        await callback_query.message.edit_text("> 💸 Economy commands:", reply_markup=keyboard)

    # Moderation menu
    elif data == "menu_moderation":
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🚫 Ban", callback_data="mod_ban"),
                 InlineKeyboardButton("🔇 Mute", callback_data="mod_mute")],
                [InlineKeyboardButton("⬅️ Back", callback_data="menu_main")]
            ]
        )
        await callback_query.message.edit_text("> 🛡 Moderation commands:", reply_markup=keyboard)

    # Music menu
    elif data == "menu_music":
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🎵 Play", callback_data="music_play"),
                 InlineKeyboardButton("⏸ Pause/Resume", callback_data="music_pause")],
                [InlineKeyboardButton("⬅️ Back", callback_data="menu_main")]
            ]
        )
        await callback_query.message.edit_text("> 🎶 Music controls:", reply_markup=keyboard)

    # Clan menu
    elif data == "menu_clan":
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🌙 Create Clan", callback_data="clan_create"),
                 InlineKeyboardButton("👥 Clan Info", callback_data="clan_info")],
                [InlineKeyboardButton("⬅️ Back", callback_data="menu_main")]
            ]
        )
        await callback_query.message.edit_text("> 🌙 Clan system:", reply_markup=keyboard)

    # Fun menu
    elif data == "menu_fun":
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("❤️ Love", callback_data="fun_love"),
                 InlineKeyboardButton("💑 Couples", callback_data="fun_couples")],
                [InlineKeyboardButton("🎭 ChatFight", callback_data="fun_chatfight")],
                [InlineKeyboardButton("⬅️ Back", callback_data="menu_main")]
            ]
        )
        await callback_query.message.edit_text("> 🌸 Fun commands:", reply_markup=keyboard)

    # Settings / main menu
    elif data == "menu_settings" or data == "menu_main":
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("⚔️ Games", callback_data="menu_games"),
                 InlineKeyboardButton("💸 Economy", callback_data="menu_economy")],
                [InlineKeyboardButton("🛡 Moderation", callback_data="menu_moderation"),
                 InlineKeyboardButton("🎶 Music", callback_data="menu_music")],
                [InlineKeyboardButton("🌙 Clan", callback_data="menu_clan"),
                 InlineKeyboardButton("🌸 Fun Zone", callback_data="menu_fun")]
            ]
        )
        await callback_query.message.edit_text("> 🌸 Welcome back to Mitsuha Game Bot main menu:", reply_markup=keyboard)

    # Answer callback to remove loading icon
    await callback_query.answer()
