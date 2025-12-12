import requests
from plugins.music.youtube import get_youtube_audio

CLIENT_ID = "YOUR_SOUNDCLOUD_CLIENT_ID"

def get_soundcloud_audio(url: str):
    # Resolve track info
    r = requests.get(f"https://api.soundcloud.com/resolve?url={url}&client_id={CLIENT_ID}")
    data = r.json()
    # Use track title & artist to search YouTube for streaming
    query = f"{data['title']} {data['user']['username']}"
    return get_youtube_audio(query)
