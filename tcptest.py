import socketserver
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()
scope = "user-read-currently-playing"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, open_browser=False))

def check_login():
    auth = sp.auth_manager
    token = auth.validate_token(auth.cache_handler.get_cached_token())
    if token is not None:
        if auth.is_token_expired(token):
            auth.refresh_access_token(token["refresh_token"])
        return True
    return False

class MyTCP(socketserver.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        # handle requests
        if self.data.startswith(b"LOGIN"):
            if check_login():
                self.request.sendall(bytes(f"CACHED:{sp.me()['display_name']}", "utf-8"))
            else:
                url = sp.auth_manager.get_authorize_url()
                self.request.sendall(bytes(url, "utf-8"))
        elif self.data.startswith(b"REDIR"):
            url = self.data.split(b":", 1)[1].decode("utf-8")
            try:
                code = sp.auth_manager.parse_response_code(url)
                sp.auth_manager.get_access_token(code, as_dict=False)
                if check_login():
                    self.request.sendall(bytes(str(f"LOGGEDIN:{sp.me()['display_name']}"), "utf-8"))
                else:
                    self.request.sendall(b"login failed: login not set")
            except spotipy.SpotifyOauthError as e:
                self.request.sendall(bytes(f"login failed: {e.error_description}", "utf-8"))
        else:
            self.request.sendall(b"wrong request")


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9999
    server = socketserver.TCPServer((HOST, PORT), MyTCP)
    print("Starting TCP server")
    server.serve_forever()
