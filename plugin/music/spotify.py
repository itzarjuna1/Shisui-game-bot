import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from plugins.music.youtube import get_youtube_audio

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id="YOUR_SPOTIFY_CLIENT_ID",
    client_secret="YOUR_SPOTIFY_CLIENT_SECRET"
))

def get_spotify_track_audio(spotify_url: str):
    track = sp.track(spotify_url)
    # Use track name + artist to search on YouTube for playback
    query = f"{track['name']} {track['artists'][0]['name']}"
    return get_youtube_audio(query)

def get_spotify_playlist_audio(playlist_url: str):
    playlist = sp.playlist_items(playlist_url)
    tracks = []
    for item in playlist['items']:
        track = item['track']
        query = f"{track['name']} {track['artists'][0]['name']}"
        tracks.append(get_youtube_audio(query))
    return tracks
