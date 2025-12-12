from yt_dlp import YoutubeDL

ydl_opts = {"format": "bestaudio", "quiet": True}

def get_youtube_audio(query: str):
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        url = info["url"]
        title = info.get("title", "Unknown")
        duration = info.get("duration", 0)
        return {"url": url, "title": title, "duration": duration}
