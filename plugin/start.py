from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from core.config import Config

app: Client = Client._global_client if hasattr(Client, "_global_client") else None

@Client.on_message(filters.command("start"))
async def start_cmd(client, message):
    # Blockquote style welcome
    text = (
        "> 🌸 Kᴏɴ'ɴɪᴄʜɪᴡᴀ… I’ᴍ Mɪᴛsᴜʜᴀ, ʏᴏᴜʀ ɢᴇɴᴛʟᴇ ɢᴀᴍᴇ & ᴜᴛɪʟɪᴛʏ ᴘᴀʀᴛɴᴇʀ~\n"
        "> Cʜᴏᴏsᴇ ᴡʜᴀᴛ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴇxᴘʟᴏʀᴇ ᴛᴏᴅᴀʏ💗"
    )

    # Inline buttons menu
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⚔️ ɢᴀᴍᴇs", callback_data="menu_games"),
             InlineKeyboardButton("💸 ᴇᴄᴏɴᴏᴍʏ", callback_data="menu_economy")],
            [InlineKeyboardButton("🛡 ᴍᴏᴅᴇʀᴀᴛɪᴏɴ", callback_data="menu_moderation"),
             InlineKeyboardButton("🎶 ᴍᴜsɪᴄ", callback_data="menu_music")],
            [InlineKeyboardButton("🌙 ᴄʟᴀɴ", callback_data="menu_clan"),
             InlineKeyboardButton("🌸 ғᴜɴ ᴢᴏɴᴇ", callback_data="menu_fun")],
            [InlineKeyboardButton("⚙️ sᴇᴛᴛɪɴɢs", callback_data="menu_settings")]
        ]
    )

    await message.reply_text(text, reply_markup=keyboard, parse_mode="markdown")
