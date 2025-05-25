from flask import Flask, request, redirect
import requests
import urllib.parse
from dotenv import load_dotenv
import urllib.parse
import base64
import os

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SCOPE = os.getenv("SPOTIFY_SCOPE")



app = Flask(__name__)
auth_code = None
access_token = None

def get_token_via_browser():
    print("Starting Spotify authentication...")

    # Step 1: Build the authorization URL
    auth_url = 'https://accounts.spotify.com/authorize'
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE,
        'show_dialog': 'true'
    }
    full_auth_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
    print("Please authorize Spotify access by visiting this URL:\n", full_auth_url)

    # Step 2: Wait for user to paste the redirected URL with `code` param
    redirected_url = input("\nAfter authorizing, paste the full redirect URL here:\n")
    parsed_url = urllib.parse.urlparse(redirected_url)
    code = urllib.parse.parse_qs(parsed_url.query).get('code', [None])[0]

    if not code:
        raise Exception("Authorization failed")

    # Step 3: Exchange code for access token
    token_url = 'https://accounts.spotify.com/api/token'
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }

    response = requests.post(token_url, headers=headers, data=data)
    token_info = response.json()

    if 'access_token' not in token_info:
        raise Exception(f"Failed to get access")

    return token_info['access_token']


class SpotifyClient(object):
    def __init__(self, api_token):
        if api_token:
            self.api_token = api_token
        else:
            self.api_token = get_token_via_browser()
    
    def search_song(self, artist, track):
        query = urllib.parse.quote(f'{artist}{track}')
        url = f"https://api.spotify.com/v1/search?q={query}&type=track"
        response = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_token}"
            }
        )
        response = response.json()

        results = response['tracks']['items']

        if results:
            # Assuming the first song is the song which we want
            return results[0]['id']
        else:
            raise Exception(f"No song found for {artist}={track}")
        
    def add_song_to_spotify(self, song_id):
        url = "https://api.spotify.com/v1/me/tracks"
        response = requests.put(
            url,
            json = {
                "ids": [song_id]
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_token}"
            }
        )

        return response.ok