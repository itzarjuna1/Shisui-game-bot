from plugins.music.youtube import get_youtube_audio

def get_resso_audio(track_name: str, artist: str):
    query = f"{track_name} {artist} site:youtube.com"
    return get_youtube_audio(query)
