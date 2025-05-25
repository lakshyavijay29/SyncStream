import os

from spotify_client import SpotifyClient
from youtube_client import YouTubeClient


def run():
    # 1. Get a list of our playlists from Youtube
    youtube_client = YouTubeClient('./creds/client_secret.json')
    spotify_client = SpotifyClient(os.getenv('SPOTIFY_AUTH_TOKEN'))
    playlists = youtube_client.get_playlists()

    # 2. Ask which playlist we want to get the music videos from 
    for index,playlist in enumerate(playlists):
        print(f"{index}: {playlist.title}")
    choice = int(input("Enter your choice: "))
    chosen_playlist = playlists[choice]
    print(f"You selected: {chosen_playlist.title}")

    # 3. For each video in the playlist, get the song information from YouTube
    songs = youtube_client.get_videos_from_playlist(chosen_playlist.id)
    print(f"Attempting to add {len(songs)}")

    # 4. Search for the song on spotify
    for song in songs:
        spotfiy_song_id = spotify_client.search_song(song.artist, song.track)
        if spotfiy_song_id:
            added_song = spotify_client.add_song_to_spotify(spotfiy_song_id)
            if added_song:
                print(f"Added {song.artist}")

if __name__ == '__main__':
    run()