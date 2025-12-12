# ============================================
# File: /plugins/utilities.py
# ============================================

# -----------------------------
# Fancy font mapper
# -----------------------------
def mitsuha_font(text: str) -> str:
    """
    Converts normal text to a decorative Mitsuha/Shisui-style font.
    """
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    fancy  = "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢᴬᴮᴰᴱᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾᴿˢᵀᵁⱽᵂˣʸᶻ"
    trans = {ord(n): ord(f) for n, f in zip(normal, fancy)}
    return text.translate(trans)


# -----------------------------
# Blockquote formatting
# -----------------------------
def blockquote(text: str) -> str:
    """
    Adds Telegram markdown blockquote to each line.
    """
    lines = text.split("\n")
    quoted = "\n".join([f"> {line}" for line in lines])
    return quoted


# -----------------------------
# Example helper: safe mention
# -----------------------------
def mention(user_id: int, name: str) -> str:
    return f"[{name}](tg://user?id={user_id})"
