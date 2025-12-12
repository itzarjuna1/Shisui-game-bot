from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# YOU CAN EDIT THESE
OWNER_NAME = "Your Name"
SUPPORT_GROUP = "https://t.me/dark_musicsupport"
CHANNEL_LINK = "https://t.me/dark_musictm"


def music_buttons(video_id: str):
    """Main music control buttons"""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⏸ Pause", callback_data=f"pause[{video_id}]"),
                InlineKeyboardButton("▶️ Resume", callback_data=f"resume[{video_id}]"),
            ],
            [
                InlineKeyboardButton("⏭ Skip", callback_data=f"skip[{video_id}]"),
                InlineKeyboardButton("⏹ Stop", callback_data=f"stop[{video_id}]"),
            ],
            [
                InlineKeyboardButton("⭐ Support", url=SUPPORT_GROUP),
                InlineKeyboardButton("📢 Channel", url=CHANNEL_LINK),
            ],
            [
                InlineKeyboardButton(f"Made by {OWNER_NAME}", url=CHANNEL_LINK)
            ]
        ]
    )
