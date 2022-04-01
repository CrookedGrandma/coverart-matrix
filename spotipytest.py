import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
load_dotenv()

scope = "user-read-currently-playing"
# scope = "user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

track = sp.current_user_playing_track()
imgurl = track["item"]["album"]["images"][2]["url"]
