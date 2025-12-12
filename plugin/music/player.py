import os
import time
import asyncio
import tempfile
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

import yt_dlp as ytdlp
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.exceptions import NoActiveGroupCall

from core.client import assistant, mongodb  # assistant Client defined in core.client
from core.config import Config

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# -------------------------
# Configuration / constants
# -------------------------
DOWNLOADS_DIR = os.path.join("downloads", "music")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

YTDL_OPTS = {
    "format": "bestaudio/best",
    "outtmpl": os.path.join(DOWNLOADS_DIR, "%(id)s.%(ext)s"),
    "noplaylist": False,
    "quiet": True,
    "no_warnings": True,
    # cookiefile support if provided
    **({"cookiefile": Config.YT_COOKIES} if getattr(Config, "YT_COOKIES", "") else {}),
}

OWNER_NAME = getattr(Config, "BOT_NAME", "Mitsuha Game Bot")
SUPPORT_URL = os.getenv("SUPPORT_URL", "https://t.me/YourSupportGroup")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/YourChannel")

# initialize pytgcalls with assistant client
pytgcalls = PyTgCalls(assistant)

# -------------------------
# Track dataclass
# -------------------------
@dataclass
class Track:
    source: str                    # original query or link
    title: str
    duration: int                  # seconds
    file_path: str                 # local file path
    requested_by: int
    yt_info: Dict[str, Any] = field(default_factory=dict)
    added_at: float = field(default_factory=time.time)
    message_id: Optional[int] = None   # now playing message id (if any)
    chat_id: Optional[int] = None

# -------------------------
# Player state
# -------------------------
QUEUES: Dict[int, List[Track]] = {}
CURRENT: Dict[int, Optional[Track]] = {}
PLAY_LOCKS: Dict[int, asyncio.Lock] = {}
NOWPLAY_MESSAGES: Dict[int, int] = {}  # chat_id -> message_id of now playing

# -------------------------
# yt-dlp helpers
# -------------------------
def _ydl_extract(query: str, download: bool = True) -> Dict[str, Any]:
    opts = dict(YTDL_OPTS)
    # if we expect a search, use ytsearch: prefix
    if not (query.startswith("http://") or query.startswith("https://")) and not query.startswith("ytsearch:"):
        # attempt search on youtube
        query = f"ytsearch:{query}"
    if not download:
        opts["noplaylist"] = True
        with ytdlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(query, download=False)
    else:
        with ytdlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(query, download=True)

def download_track_sync(query: str) -> Track:
    info = _ydl_extract(query, download=True)
    # If the query was a search result, info could be a 'entries' list
    if isinstance(info, dict) and info.get("entries"):
        # take first entry
        info = info["entries"][0]
    video_id = info.get("id") or str(int(time.time()))
    ext = info.get("ext") or "m4a"
    expected_path = os.path.join(DOWNLOADS_DIR, f"{video_id}.{ext}")
    # If yt-dlp used outtmpl as above, file should exist
    if not os.path.exists(expected_path):
        # attempt to find a downloaded file by searching downloads dir
        for f in os.listdir(DOWNLOADS_DIR):
            if f.startswith(video_id):
                expected_path = os.path.join(DOWNLOADS_DIR, f)
                break
    title = info.get("title", "Unknown")
    duration = int(info.get("duration") or 0)
    return Track(source=query, title=title, duration=duration, file_path=expected_path, requested_by=0, yt_info=info)

# -------------------------
# Progress bar helper
# -------------------------
def progress_bar(elapsed: int, total: int, length: int = 20) -> str:
    if total <= 0:
        return "▮" * length
    filled = int(length * elapsed / total)
    bar = "█" * filled + "—" * (length - filled)
    return f"[{bar}] {elapsed // 60}:{elapsed % 60:02d}/{total // 60}:{total % 60:02d}"

# -------------------------
# Inline buttons builder
# -------------------------
def build_nowplaying_keyboard(track: Track):
    vid_tag = os.path.basename(track.file_path) if track.file_path else str(int(time.time()))
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⏯️ Pause/Resume", callback_data=f"music_toggle[{vid_tag}]"),
                InlineKeyboardButton("⏭ Skip", callback_data=f"music_skip[{vid_tag}]"),
            ],
            [
                InlineKeyboardButton("⏹ Stop", callback_data=f"music_stop[{vid_tag}]"),
                InlineKeyboardButton("🔁 Queue", callback_data=f"music_queue[{vid_tag}]"),
            ],
            [
                InlineKeyboardButton("💬 Support", url=SUPPORT_URL),
                InlineKeyboardButton("📢 Channel", url=CHANNEL_URL),
            ],
            [
                InlineKeyboardButton(f"Made by {OWNER_NAME}", url=CHANNEL_URL)
            ]
        ]
    )

# -------------------------
# Public API
# -------------------------
async def enqueue(chat_id: int, query: str, requested_by: int) -> Track:
    """
    Download+enqueue a track for given chat.
    Returns Track object.
    """
    # Ensure queue and lock exist
    QUEUES.setdefault(chat_id, [])
    PLAY_LOCKS.setdefault(chat_id, asyncio.Lock())

    # Download track in executor to avoid blocking event loop
    loop = asyncio.get_event_loop()
    track: Track = await loop.run_in_executor(None, download_track_sync, query)
    track.requested_by = requested_by
    track.chat_id = chat_id

    QUEUES[chat_id].append(track)
    # Start play loop if not running
    if not CURRENT.get(chat_id):
        asyncio.create_task(_play_loop(chat_id))
    return track

async def get_queue(chat_id: int) -> List[Track]:
    return QUEUES.get(chat_id, []).copy()

async def now_playing(chat_id: int) -> Optional[Track]:
    return CURRENT.get(chat_id)

async def skip(chat_id: int) -> bool:
    """
    Skip currently playing track by leaving the group call.
    Returns True if skip initiated.
    """
    if CURRENT.get(chat_id):
        try:
            await pytgcalls.leave_group_call(chat_id)
        except Exception:
            pass
        return True
    return False

async def stop(chat_id: int) -> bool:
    """
    Stop playback and clear queue.
    """
    if QUEUES.get(chat_id):
        QUEUES[chat_id].clear()
    CURRENT[chat_id] = None
    try:
        await pytgcalls.leave_group_call(chat_id)
    except Exception:
        pass
    return True

async def pause(chat_id: int) -> bool:
    try:
        await pytgcalls.pause_stream(chat_id)
        return True
    except Exception:
        return False

async def resume(chat_id: int) -> bool:
    try:
        await pytgcalls.resume_stream(chat_id)
        return True
    except Exception:
        return False

# -------------------------
# Internal play loop
# -------------------------
async def _play_loop(chat_id: int):
    """
    Stream tracks from QUEUES[chat_id] sequentially.
    """
    lock = PLAY_LOCKS.setdefault(chat_id, asyncio.Lock())
    async with lock:
        # Ensure assistant/pytgcalls started
        if not assistant.is_connected:
            try:
                await assistant.start()
            except Exception:
                pass
        try:
            if not pytgcalls.is_connected:
                await pytgcalls.start()
        except Exception:
            pass

        while QUEUES.get(chat_id):
            track = QUEUES[chat_id][0]
            CURRENT[chat_id] = track
            # Send Now Playing message (attempt via assistant or bot user)
            try:
                # Try to obtain a Pyrogram client to send the message: use assistant to send status message
                sent_msg = await assistant.send_message(
                    chat_id,
                    f"> 🎵 Now Playing: **{track.title}**\n> ⏱ {track.duration // 60}:{track.duration % 60:02d}\n"
                    f"> {progress_bar(0, track.duration)}\n> Made by {OWNER_NAME}"
                )
                track.message_id = sent_msg.message_id
                NOWPLAY_MESSAGES[chat_id] = sent_msg.message_id
                # edit message later to update progress (background task)
                asyncio.create_task(_progress_updater(chat_id, track))
            except Exception:
                # if assistant cannot send, try bot client via Mongo-stored bot token? skip for now
                track.message_id = None

            # Join group call and stream file
            try:
                # ensure file exists
                if not track.file_path or not os.path.exists(track.file_path):
                    # attempt re-download
                    loop = asyncio.get_event_loop()
                    new_track = await loop.run_in_executor(None, download_track_sync, track.source)
                    track.file_path = new_track.file_path
                    track.yt_info = new_track.yt_info

                await pytgcalls.join_group_call(chat_id, AudioPiped(track.file_path))
            except NoActiveGroupCall:
                # no active vc — abort and notify
                try:
                    await assistant.send_message(chat_id, "> 🛑 No active voice chat found. Start a voice chat and re-run /play.")
                except Exception:
                    pass
                # stop playback loop
                CURRENT[chat_id] = None
                break
            except Exception as e:
                # on unexpected error remove the track and continue
                try:
                    QUEUES[chat_id].pop(0)
                except Exception:
                    pass
                CURRENT[chat_id] = None
                continue

            # Wait while the track plays (poll)
            start_time = time.time()
            while True:
                elapsed = int(time.time() - start_time)
                if track.duration and elapsed >= track.duration:
                    break
                # break condition: if track was skipped/stopped (pytgcalls left)
                await asyncio.sleep(1)
                # If pytgcalls no longer streaming in chat, break
                # (This is a best-effort approach)
            # After play done, leave group call
            try:
                await pytgcalls.leave_group_call(chat_id)
            except Exception:
                pass

            # Remove finished track from queue
            try:
                QUEUES[chat_id].pop(0)
            except Exception:
                pass
            CURRENT[chat_id] = None

        # queue empty cleanup
        CURRENT[chat_id] = None
        # optional: cleanup now-playing message (edit to show finished)
        if NOWPLAY_MESSAGES.get(chat_id):
            try:
                await assistant.edit_message_text(
                    chat_id,
                    NOWPLAY_MESSAGES[chat_id],
                    f"> ✅ Finished playing queue. Made by {OWNER_NAME}"
                )
            except Exception:
                pass
            NOWPLAY_MESSAGES.pop(chat_id, None)

# -------------------------
# Progress updater (edits the now playing message every 5s)
# -------------------------
async def _progress_updater(chat_id: int, track: Track):
    try:
        msg_id = NOWPLAY_MESSAGES.get(chat_id)
        if not msg_id:
            return
        start = time.time()
        while CURRENT.get(chat_id) and CURRENT[chat_id] == track:
            elapsed = int(time.time() - start)
            # build progress text
            bar = progress_bar(elapsed, track.duration)
            txt = f"> 🎵 Now Playing: **{track.title}**\n> ⏱ {track.duration // 60}:{track.duration % 60:02d}\n> {bar}\n> Made by {OWNER_NAME}"
            try:
                await assistant.edit_message_text(chat_id, msg_id, txt)
            except Exception:
                pass
            await asyncio.sleep(5)
    except Exception:
        pass

# -------------------------
# Cleanup old downloads
# -------------------------
def cleanup_downloads(older_than_seconds: int = 3600 * 6):
    now = time.time()
    for fname in os.listdir(DOWNLOADS_DIR):
        try:
            path = os.path.join(DOWNLOADS_DIR, fname)
            if os.path.isfile(path) and (now - os.path.getmtime(path)) > older_than_seconds:
                os.remove(path)
        except Exception:
            pass

# -------------------------
# Graceful shutdown helper
# -------------------------
async def shutdown():
    try:
        await pytgcalls.stop()
    except Exception:
        pass
    try:
        await assistant.stop()
    except Exception:
        pass
```0
