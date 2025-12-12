import os
import asyncio
import tempfile
import shutil
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

import yt_dlp as ytdlp
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.exceptions import NoActiveGroupCall
from core.client import assistant, mongodb  # assistant Client is defined in core.client
from core.config import Config

# initialize pytgcalls with assistant client
pytgcalls = PyTgCalls(assistant)

# download dir
DOWNLOADS_DIR = os.path.join("downloads", "music")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# yt-dlp options (stream-safe)
YTDL_OPTS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "outtmpl": os.path.join(DOWNLOADS_DIR, "%(id)s.%(ext)s"),
    # use a cookies file if provided (for region-locked YouTube)
    **({"cookiefile": Config.YT_COOKIES} if getattr(Config, "YT_COOKIES", "") else {}),
}

@dataclass
class Track:
    source: str              # original query or link
    title: str
    duration: int            # seconds
    file_path: str           # local file path to audio
    requested_by: int
    started_at: Optional[float] = None
    yt_info: Dict[str, Any] = field(default_factory=dict)


# per-chat queues
QUEUES: Dict[int, List[Track]] = {}
# playing state locks so only single play loop per chat runs
PLAY_LOCKS: Dict[int, asyncio.Lock] = {}
# simple in-memory map of currently playing track for status/progress
CURRENT: Dict[int, Optional[Track]] = {}

# -------------------------
# Utility / download
# -------------------------
async def yt_download(query: str) -> Track:
    """
    Download given query (yt search or direct link) using yt-dlp and return a Track.
    This function is synchronous for yt-dlp, so run in executor.
    """
    loop = asyncio.get_event_loop()
    info = await loop.run_in_executor(None, _ydl_extract, query)
    # pick best audio file path from info
    # ytdlp outtmpl uses id and ext so extract filename
    file_path = None
    if isinstance(info, dict):
        # preferred filename: ytdl puts path in 'requested_downloads' or we can compute from id/ext
        ext = info.get("ext") or "m4a"
        video_id = info.get("id") or str(time.time()).replace(".", "")
        candidate = os.path.join(DOWNLOADS_DIR, f"{video_id}.{ext}")
        if os.path.exists(candidate):
            file_path = candidate
    # fallback: if info provides url (direct stream), we still need a local file to stream via AudioPiped
    if not file_path:
        # try to download explicitly to a temp file
        temp_fd, temp_path = tempfile.mkstemp(suffix=".mp3", dir=DOWNLOADS_DIR)
        os.close(temp_fd)
        # re-run ytdlp to download to temp_path
        ydl_opts = dict(YTDL_OPTS)
        ydl_opts.update({"outtmpl": temp_path, "noplaylist": True})
        await loop.run_in_executor(None, _ydl_download_to, query, ydl_opts)
        file_path = temp_path

    title = info.get("title", "Unknown")
    duration = int(info.get("duration", 0) or 0)
    requested_by = 0  # caller should set this after download
    return Track(source=query, title=title, duration=duration, file_path=file_path, requested_by=requested_by, yt_info=info)


def _ydl_extract(query: str):
    with ytdlp.YoutubeDL(YTDL_OPTS) as ydl:
        return ydl.extract_info(query, download=True)  # download=True to ensure file exists


def _ydl_download_to(query: str, ydl_opts: Dict):
    with ytdlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(query, download=True)


# -------------------------
# Queue management API
# -------------------------
async def enqueue(chat_id: int, query: str, requested_by: int) -> Track:
    """
    Download and enqueue a track for the chat.
    Returns the Track object.
    """
    # ensure queue exists
    if chat_id not in QUEUES:
        QUEUES[chat_id] = []
    if chat_id not in PLAY_LOCKS:
        PLAY_LOCKS[chat_id] = asyncio.Lock()

    # download (may take time) -- run without holding the play lock
    track = await yt_download(query)
    track.requested_by = requested_by

    QUEUES[chat_id].append(track)
    # if not currently playing, start the play loop
    if not CURRENT.get(chat_id):
        # create task to handle playback (do not await here)
        asyncio.create_task(_play_loop(chat_id))
    return track


async def get_queue(chat_id: int) -> List[Track]:
    return QUEUES.get(chat_id, [])


async def skip(chat_id: int) -> bool:
    """
    Skip current track. Returns True if skipped, False if nothing to skip.
    """
    # stopping group call playback by leaving/rejoining is handled in play loop
    if CURRENT.get(chat_id):
        # Mark current track as finished by cancelling playback via pytgcalls
        try:
            await pytgcalls.leave_group_call(chat_id)
        except Exception:
            pass
        return True
    return False


async def stop(chat_id: int) -> None:
    """
    Stop playback and clear queue for chat.
    """
    QUEUES[chat_id] = []
    CURRENT[chat_id] = None
    try:
        await pytgcalls.leave_group_call(chat_id)
    except Exception:
        pass


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
    Main per-chat playback loop. Downloads already done in enqueue.
    Streams files via AudioPiped and manages CURRENT/QUEUES state.
    """
    # ensure assistant/pytgcalls is started
    if not assistant.is_connected:
        await assistant.start()
    if not pytgcalls.is_connected:
        await pytgcalls.start()

    lock = PLAY_LOCKS.setdefault(chat_id, asyncio.Lock())
    async with lock:
        while QUEUES.get(chat_id):
            track = QUEUES[chat_id][0]
            CURRENT[chat_id] = track
            track.started_at = time.time()

            # attempt to join & stream
            try:
                # ensure file exists
                if not os.path.exists(track.file_path):
                    # if file missing, try re-download
                    t2 = await yt_download(track.source)
                    track.file_path = t2.file_path

                # join and stream
                await pytgcalls.join_group_call(chat_id, AudioPiped(track.file_path))
            except NoActiveGroupCall:
                # There's no active group call in the chat - we should notify and abort playback
                # leave CURRENT and stop playback loop
                CURRENT[chat_id] = None
                break
            except Exception:
                # on error, remove track and continue
                try:
                    QUEUES[chat_id].pop(0)
                except Exception:
                    pass
                CURRENT[chat_id] = None
                continue

            # sleep for duration but wake early if track file removed / skip called
            start = time.time()
            while True:
                elapsed = time.time() - start
                if track.duration and elapsed >= track.duration:
                    break
                # if skip requested by external leave_group_call, the call may end — check call status
                # simplest approach: poll every second
                await asyncio.sleep(1)
                # if the group call is not active anymore, break
                # PyTgCalls does not expose easy per-chat active check; attempt to continue nonetheless

            # finished playback for this track
            try:
                # leave call to ensure clean state before next track
                await pytgcalls.leave_group_call(chat_id)
            except Exception:
                pass

            # remove finished track
            try:
                QUEUES[chat_id].pop(0)
            except Exception:
                pass

            CURRENT[chat_id] = None

        # cleanup: when queue empty
        CURRENT[chat_id] = None


# -------------------------
# Cleanup helper
# -------------------------
def cleanup_downloads(older_than_seconds: int = 3600):
    """
    Delete downloaded files older than given seconds to avoid disk bloat.
    """
    now = time.time()
    for fname in os.listdir(DOWNLOADS_DIR):
        path = os.path.join(DOWNLOADS_DIR, fname)
        try:
            mtime = os.path.getmtime(path)
            if now - mtime > older_than_seconds:
                os.remove(path)
        except Exception:
            pass
