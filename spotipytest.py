import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
load_dotenv()

scope = "user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

track = sp.track("https://open.spotify.com/track/6G8sFs8Nw2yQ6zHLmSSb7r?si=9e4ef55df05b4338")
imgurl = track["album"]["images"][2]
