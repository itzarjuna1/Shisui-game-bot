# Apple Music does not provide direct free streams
# We search Apple Music track on YouTube
from plugins.music.youtube import get_youtube_audio

def get_apple_music_audio(track_name: str, artist: str):
    query = f"{track_name} {artist} site:youtube.com"
    return get_youtube_audio(query)
